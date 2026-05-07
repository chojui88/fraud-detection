"""
api.py — FastAPI 后端接口

作用：
  提供 HTTP 接口，让前端（React）可以查询交易数据和统计信息。

什么是 FastAPI？
  - Python 的 Web 框架，用来快速搭建 API。
  - 前端通过 HTTP 请求访问这里的接口，拿到数据后渲染到页面。

接口列表：
  GET /transactions  → 返回最近的交易列表（含欺诈判断结果）
  GET /stats         → 返回统计信息（总数、欺诈数、正常数、欺诈率）
  GET /health        → 健康检查（确认服务在运行）
"""

import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import consumer  # 导入消费者模块，共用 results 列表

# ─── 创建 FastAPI 应用 ────────────────────────────────────────────────────────
app = FastAPI(title="支付欺诈检测 API")

# ─── 允许跨域（让 React 前端可以访问这个 API）────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有来源（开发阶段用，生产环境要限制）
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """健康检查接口 — 前端可以用这个确认后端是否在线"""
    return {"status": "ok", "message": "欺诈检测服务运行中"}


@app.get("/transactions")
def get_transactions(limit: int = 50):
    """
    返回最近的交易记录。
    参数：
      limit — 返回几条，默认50条（前端可以传 ?limit=100 来调整）
    """
    with consumer.results_lock:
        # 取最新的 limit 条，倒序（最新的在前面）
        recent = list(reversed(consumer.results[-limit:]))
    return {"data": recent, "count": len(recent)}


@app.get("/stats")
def get_stats():
    """
    返回统计信息，供前端绘制图表使用。
    """
    with consumer.results_lock:
        all_results = list(consumer.results)

    total = len(all_results)
    fraud_count = sum(1 for r in all_results if r["isFraud"])
    normal_count = total - fraud_count
    fraud_rate = round(fraud_count / total * 100, 2) if total > 0 else 0

    return {
        "total": total,           # 总交易数
        "fraudCount": fraud_count,  # 欺诈交易数
        "normalCount": normal_count,  # 正常交易数
        "fraudRate": fraud_rate,    # 欺诈率（百分比）
    }


def main():
    """
    启动入口：
    1. 在后台线程中启动 Kafka 消费者（持续接收数据）
    2. 在主线程中启动 FastAPI 服务（提供 HTTP 接口）
    """
    # 在后台线程启动 Kafka 消费者（不阻塞主线程）
    t = threading.Thread(target=consumer.start_consumer, daemon=True)
    t.start()

    # 启动 API 服务，端口 8000
    print("🚀 API 服务启动中，访问 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
