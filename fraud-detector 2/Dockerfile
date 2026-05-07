FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir kafka-python-ng fastapi==0.111.0 uvicorn==0.29.0 \
    numpy scikit-learn pandas joblib

# 소스 복사
COPY . .

EXPOSE 8000

CMD ["python", "api.py"]
