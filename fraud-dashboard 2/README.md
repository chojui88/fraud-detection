# fraud-dashboard — 실시간 사기 탐지 대시보드

## 시작 방법

```bash
# 1. 의존성 설치
npm install

# 2. 개발 서버 시작
npm start
# 브라우저에서 http://localhost:3000 열기
```

## 실행 순서 (전체 시스템)

1. Kafka 실행
2. 팀원의 payment-generator 실행 (포트 8081)
3. fraud-detector 실행: `python api.py` (포트 8000)
4. fraud-dashboard 실행: `npm start` (포트 3000)
