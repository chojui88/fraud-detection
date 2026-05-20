#train.py - payment-generator로 생성된 데이터로 학습

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# ── 1. 데이터 읽기 ──────────────────────────────────────────────
print("Payment_data.csv 읽는 중,,, / Loading payment_data.csv...")
df = pd.read_csv("payment_data.csv")

fraud_count = df['isFraud'].sum()
normal_count = (df['isFraud'] == 0).sum()
print(f"   총 데이터 / Total: {len(df):,}건 | 사기 / Fraud: {fraud_count:,}건({fraud_count/len(df)*100:.1f}%) | 정상 / Normal: {normal_count:,}건")

# ── 2. 특징 추출 / Feature Extraction ────────────────────────────────────────
if 'freq_score' not in df.columns:
    df['freq_score'] = 0.0        

features = ['amount', 'hour', 'ip_last', 'device_num', 'freq_score', 'failed_count']  
X = df[features]
y = df['isFraud']

print(f"\n 사용 특징 / Features ({len(features)}개) : {features}")

# ── 3. 학습 / 테스트 분리 / Train-Test Split ─────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"    학습 / Train: {len(X_train):,}건 | 테스트 / Test: {len(X_test):,}건")

# ──  SMOTE 오버샘플링 ──────────────────────────────────────── 
print("\n⚖️  SMOTE 오버샘플링 중... / Applying SMOTE...")
sm = SMOTE(random_state=42, k_neighbors=5)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)
fraud_res = y_train_res.sum()
print(f"   샘플링 후 / After SMOTE → 정상: {(y_train_res==0).sum():,}건 | 사기: {fraud_res:,}건")

# ── 4. 모델 학습 / Model Training ────────────────────────────────────────────
print("\n🤖 Random Forest 학습 중... / Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    class_weight='balanced', # 사기 5% 불균형 보정 / Fraud 5% imbalance correction
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_res, y_train_res)
print("   학습 완료! / Training complete!")

# ── 5. 성능 평가 / Model Evaluation ──────────────────────────────────────────
print("\n📊 테스트 데이터 평가 중... / Evaluating on test data...")

THRESHOLD = 0.50  # 올릴수록 더 정상을 사기라고 판단                            
y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= THRESHOLD).astype(int)

print("\n🔍 threshold별 정확도 변화:")
for t in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80]:
    y_pred_t = (y_prob >= t).astype(int)
    acc_t = accuracy_score(y_test, y_pred_t)
    fraud_pred = y_pred_t.sum()
    print(f"   threshold={t:.2f} → 정확도: {acc_t*100:.2f}% | 사기판정: {fraud_pred}건")

acc = accuracy_score(y_test, y_pred)
print(f"\n✅ 정확도 / Accuracy: {acc*100:.2f}%  (threshold={THRESHOLD})")
print("\n📋 상세 리포트 / Classification Report:")
print(classification_report(y_test, y_pred, target_names=["정상 / Normal", "사기 / Fraud"]))

# ── 6. 특징 중요도 / Feature Importance ──────────────────────────────────────
importances = model.feature_importances_
print("\n📈 특징 중요도 / Feature Importance:")
for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
    print(f"   {feat:15s}: {imp:.4f}")

# ── 7. 모델 저장 / Save Model ─────────────────────────────────────────────────
joblib.dump(model, "fraud_model.pkl")
joblib.dump(THRESHOLD, "threshold.pkl")   
print("\n💾 모델 저장 완료 / Model saved: fraud_model.pkl")
print("🎉 완료 / Done! detector.py 실행하면 새 모델 자동 로드됩니다. / New model will be loaded automatically.")