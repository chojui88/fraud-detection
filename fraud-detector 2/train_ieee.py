"""
train_ieee.py — IEEE-CIS 실제 거래 데이터로 모델 학습

데이터: Kaggle IEEE-CIS Fraud Detection
  - Vesta Corporation 제공 실제 결제 데이터
  - 총 약 59만 건, 사기율 약 3.5% (현실적인 비율)
  - 합성 데이터와 달리 실제 패턴 반영

특징 매핑 (실시간 시스템의 6개 특징과 동일):
  TransactionAmt → amount       (거래금액)
  TransactionDT  → hour         (거래시간 0~23)
  addr1 % 256    → ip_last      (청구지 코드 기반 수치)
  ProductCD      → device_num   (거래 채널: W/H/C/S/R)
  C1             → freq_score   (카드 관련 거래 빈도 카운트)
  C6             → failed_count (실패 거래 관련 카운트)
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

# ── 1. 데이터 읽기 ─────────────────────────────────────────────────────────────
print("📂 train_transaction.csv 읽는 중... (시간이 걸릴 수 있습니다)")
df = pd.read_csv("train_transaction.csv")
fraud_count = df['isFraud'].sum()
normal_count = (df['isFraud'] == 0).sum()
print(f"   총 데이터: {len(df):,}건  |  사기: {fraud_count:,}건({fraud_count/len(df)*100:.1f}%)  |  정상: {normal_count:,}건")

# ── 2. 실시간 시스템과 동일한 6개 특징 추출 ────────────────────────────────────
print("\n🔧 6개 특징 추출 중...")

# amount — 거래금액
df['amount'] = df['TransactionAmt']

# hour — 거래 시간대 (TransactionDT는 초 단위 경과시간, 86400초=하루)
df['hour'] = (df['TransactionDT'] % 86400) // 3600

# ip_last — 청구지 주소 코드 기반 수치 (IP 마지막 숫자 대체)
df['ip_last'] = df['addr1'].fillna(0).astype(int) % 256

# device_num — 거래 채널 종류 (W=0, H=1, C=2, S=3, R=4)
product_map = {'W': 0, 'H': 1, 'C': 2, 'S': 3, 'R': 4}
df['device_num'] = df['ProductCD'].map(product_map).fillna(0).astype(int)

# freq_score — 카드 관련 거래 빈도 (C1: count feature)
df['freq_score'] = df['C1'].fillna(0)

features = ['amount', 'hour', 'ip_last', 'device_num', 'freq_score']
X = df[features]
y = df['isFraud']

print(f"   사용 특징 ({len(features)}개): {features}")

# ── 3. 학습 / 테스트 분리 ──────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   학습 데이터: {len(X_train):,}건  |  테스트 데이터: {len(X_test):,}건")

# ── 4. 모델 학습 (class_weight='balanced': 사기 데이터 적어도 공정하게 학습) ──
print("\n🤖 Random Forest 모델 학습 중... (시간이 걸릴 수 있습니다)")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    class_weight='balanced',   # 사기 3.5% 불균형 보정
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("   학습 완료!")

# ── 5. 정확도 평가 ────────────────────────────────────────────────────────────
print("\n📊 테스트 데이터로 평가 중...")
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print(f"\n✅ 정확도 (Accuracy): {acc*100:.2f}%")
print("\n📋 상세 리포트:")
print(classification_report(y_test, y_pred, target_names=["정상", "사기"]))

# ── 6. 특징 중요도 출력 ──────────────────────────────────────────────────────
importances = model.feature_importances_
print("\n📈 특징 중요도:")
for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
    print(f"   {feat:15s}: {imp:.4f}")

# ── 7. 모델 저장 ──────────────────────────────────────────────────────────────
joblib.dump(model, "fraud_model.pkl")
print("\n💾 모델 저장 완료: fraud_model.pkl")
print("\n🎉 완료! IEEE-CIS 실제 데이터 기반 Random Forest 모델 저장됨.")
print("   api.py 재시작하면 자동으로 로드됩니다.")
