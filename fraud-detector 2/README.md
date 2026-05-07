# fraud-detector — 支付欺诈检测服务

## 启动步骤

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 确保 Kafka 已在运行（和队友的项目共用同一个 Kafka）

# 3. 启动服务
python api.py
```

## 接口

| 接口 | 说明 |
|------|------|
| GET http://localhost:8000/health | 确认服务在线 |
| GET http://localhost:8000/transactions | 最近交易列表 |
| GET http://localhost:8000/stats | 统计数据（欺诈率等） |
