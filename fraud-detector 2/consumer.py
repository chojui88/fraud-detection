"""
Kafka 消费者 + 欺诈检测核心 사기 탐지

改进内容：
  新增「短时间高频交易检测」
  - 记录每个账户/设备最近60秒内的交易次数 기기별로 최근 60초 거래 횟수
  - 次数越多，freq_score（频率分数）越高 거래 횟수 많을수록 빈도점수 추가
  - freq_score >= 5 时，detector.py 会强制判定为欺诈 5 이상이면 사기!
"""

import json
import os
import threading
import time
from collections import defaultdict #딕셔너리 도구, 없는키 기본값 생성
from kafka import KafkaConsumer
from detector import FraudDetector

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# ─── 全局存储 전역 저장공간───────────────────────────────────────────────────────────────
results = []
results_lock = threading.Lock() 
MAX_RESULTS = 1000

# ─── 고빈도 거래 추적용 데이터 구조 ──────────────────────────────────────────
# 각 계좌/기기별로 최근 거래 시간들을 기록
account_timestamps = defaultdict(list)   # { "accountNo": [timestamp1, timestamp2, ...] }
device_timestamps  = defaultdict(list)   # { "deviceId":  [timestamp1, timestamp2, ...] }
freq_lock = threading.Lock()
FREQ_WINDOW = 60   # 60초 안에 몇 번 거래했는지 체크

# ─── 초기화 ──────────────────────────────────────────────────────────────────
detector = FraudDetector()


def _calc_freq_score(event: dict) -> float:
    """
    짧은 시간 안에 거래가 얼마나 자주 발생했나 점수로 계산하느 함수

    작동 원리:
      1. 이 거래의 계좌번호/기기ID로 최근 60초 이내 거래 횟수를 조회
      2. 계좌 횟수 + 기기 횟수를 합산해 freq_score 반환
      3. freq_score >= 5 이면 detector.py에서 사기로 판정

    예시:    FREQ_WINDOW = 60   # 60초 안에 몇 번 거래했는지 체크
      같은 계좌에서 60초 안에 4번 거래 + 같은 기기에서 3번 거래
      → freq_score = 4 + 3 = 7  → 사기 판정
    """
    now = time.time()
    account = event.get("accountNo", "")
    device  = event.get("deviceId", "")

    with freq_lock:
        # 60초 지난 기록은 제거
        account_timestamps[account] = [
            t for t in account_timestamps[account] if now - t < FREQ_WINDOW
        ]
        device_timestamps[device] = [
            t for t in device_timestamps[device] if now - t < FREQ_WINDOW
        ]

        # 현재 거래 시간 기록
        account_timestamps[account].append(now)
        device_timestamps[device].append(now)

        # 점수 = 계좌 횟수 + 기기 횟수
        freq_score = len(account_timestamps[account]) + len(device_timestamps[device])

    return float(freq_score)


def start_consumer():
    """
    Kafka 消费者 시작.
    매 메시지마다:
      1. 고빈도 점수 계산
      2. 모델에 전달해 사기 여부 판단
      3. 결과를 results 리스트에 저장
    연결 실패 시 5초 후 자동 재연결.
    """
    while True:
        try:
            consumer = KafkaConsumer(
                "payment-events",
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                group_id="fraud-detector-group"
            )

            print("✅ Kafka 消费者已启动，正在监听(정상실행) payment-events ...")

            for message in consumer:
                event = message.value

                # 1. 고빈도 점수 계산
                freq_score = _calc_freq_score(event)

                # 2. 모델 판단 (freq_score도 함께 전달)
                is_fraud, score = detector.predict(event, freq_score=freq_score)

                # 3. 결과 조립
                result = {
                    **event,
                    "isFraud": is_fraud,
                    "anomalyScore": round(score, 4),
                    "freqScore": int(freq_score),   # 고빈도 점수도 프론트에 전달
                }

                with results_lock:
                    results.append(result)
                    if len(results) > MAX_RESULTS:
                        results.pop(0)

                # 로그
                freq_tag = f" ⚡고빈도({int(freq_score)})" if freq_score >= 5 else ""
                status = "🚨 欺诈(사기)" if is_fraud else "✅ 正常(정상)"
                print(f"{status}{freq_tag} | 거래ID: {event['transactionId']} | 금액: {event['amount']}원 | 점수: {score:.4f}")

        except Exception as e:
            print(f"⚠️ Kafka 消费者错误(에러발생)): {e}，5秒后重新连接(5초대기)...")
            time.sleep(5)
