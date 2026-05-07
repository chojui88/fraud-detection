"""
detector.py — 欺诈检测模型

작용：
  Random Forest 알고리즘으로 거래가 사기인지 판단。

특징 6개：
  1. amount       — 결제 금액
  2. hour         — 거래 시간 (0~23)
  3. ip_last      — IP 플래그 (데이터셋: 0/1, 실시간: IP 마지막 숫자)
  4. device_num   — 기기 번호
  5. freq_score   — 단시간 고빈도 점수
  6. failed_count — 7일 실패 거래 횟수 (이벤트에 failedCount 필드 or 기본값 0)

  ※ risk_score 제외: 데이터셋의 Risk_Score는 Fraud_Label로부터 파생된 값으로
    학습에 사용하면 데이터 누수(Data Leakage)가 발생함.
"""

import os
import numpy as np
import datetime
import joblib

# 모델 파일 경로
MODEL_PATH = "fraud_model.pkl"


class FraudDetector:
    def __init__(self): #초기화 함수
        self.model = None
        self.is_trained = False #모델 학습 여부
        self._load_model()

    # ── 모델 로드 ─────────────────────────────────────────────────────────────

    def _load_model(self):
        """
        시작 시 저장된 모델 파일을 로드한다.
        fraud_model.pkl 이 없으면 규칙 기반으로 폴백.
        """
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
                print(f"✅ 已加载保存的模型(성공): {MODEL_PATH}  (Random Forest, 7特征)")
            except Exception as e:
                print(f"⚠️  모델 로드 실패, 규칙 기반으로 폴백: {e}")
        else:
            print("⚠️  fraud_model.pkl 없음 → 규칙 기반 판단 사용")
            print("   train_ecommerce.py 를 실행하여 모델을 학습하세요.")

    # ── 특징 추출 ─────────────────────────────────────────────────────────────

    def _extract_features(self, event: dict, freq_score: float = 0.0) -> list:
        """
        결제 이벤트에서 7개 특징을 추출한다.
        """
        # 1. amount
        amount = event.get("amount", 0)

        # 2. hour
        ts = event.get("timestamp", 0) / 1000
        hour = datetime.datetime.fromtimestamp(ts).hour

        # 3. ip_last
        ip = event.get("ipAddress", "0.0.0.0")
        ip_last = int(ip.split(".")[-1]) if ip else 0

        # 4. device_num
        device = event.get("deviceId", "DEV-0")
        device_num = int(device.split("-")[-1]) if "-" in device else 0

        # 5. freq_score (파라미터로 전달)

        return [amount, hour, ip_last, device_num, freq_score]

    # ── 예측 ──────────────────────────────────────────────────────────────────

    def predict(self, event: dict, freq_score: float = 0.0):
        """
        거래가 사기인지 판단한다.

        반환: (is_fraud: bool, score: float)
        """
        features = self._extract_features(event, freq_score)

        # 고빈도 점수가 매우 높으면 즉시 사기 판정
        if freq_score >= 15:
            return True, -0.9

        if self.is_trained and self.model is not None:
            X = np.array([features])
            prediction = self.model.predict(X)[0]
            try:
                proba = self.model.predict_proba(X)[0][1]  # 사기 확률
                score = float(proba * 2 - 1)               # -1 ~ 1 범위로 변환
            except:
                score = float(prediction)
            is_fraud = bool(prediction == 1)
            return is_fraud, score
        else:
            # 모델 없으면 규칙 기반
            is_fraud = self._rule_based(event)
            return is_fraud, -0.5 if is_fraud else 0.5

    def _rule_based(self, event: dict) -> bool:
        """
        모델이 없을 때 폴백 — 모델 파일이 없으면 모두 정상으로 처리.
        """
        return False
    
    # ── Spark Streaming 실행 로직 (파일 하단에 추가) ──────────────────────────

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import udf, col, from_json 
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

    #Spark 세션 초기화
    spark = SparkSession.builder \
        .appName("FraudDetectionStream") \
        .getOrCreate()
        
    #detection 객체 생성
    detector = FraudDetector()

    #spark용 함수 정의
    def predict_logic(amount, timestamp, ip, device):
        event = {
            "amount": amount,
            "timestamp": timestamp,
            "ipAddress": ip,
            "deviceId": device
        }
       
        is_fraud, score = detector.predict(event, freq_score=0.0)
        return f"Fraud: {is_fraud} (Score: {score:.2f})"
    
    predict_udf = udf(predict_logic, StringType())

    #generator에서 보낸 데이터 구조 정의
    schema = StructType([
        StructField("transactionId", StringType()),
        StructField("userId", StringType()),
        StructField("amount", DoubleType()),
        StructField("ipAddress", StringType()),
        StructField("timestamp", LongType()),
        StructField("deviceId", StringType())
    ])

    #kafka 데이터 읽기
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "payments-topic") \
        .load()

    #json 파싱, 예측 적용
    parsed_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"),schema).alias("data")) \
        .select("data.*")
    
    result_df = parsed_df.withColumn("prediction",
        predict_udf(col("amount"), col("timestamp"), col("ipAddress"), col("deviceId")))
    
    #결과 출력
    query = result_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()
    
    
    query.awaitTermination()