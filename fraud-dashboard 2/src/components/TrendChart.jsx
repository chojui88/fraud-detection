/**
 * TrendChart.jsx — 실시간 거래량 추세 折线图
 *
 * 作用：
 *   최근 1분간의 정상 거래수와 사기 거래수를 시간별로 꺾은선 그래프로 표시.
 *   매 2초마다 App.jsx에서 새 데이터를 받아 자동 갱신.
 *
 * props:
 *   transactions — 최근 거래 배열 (App.jsx에서 전달)
 */

import { useMemo } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from "recharts";

export default function TrendChart({ transactions }) {
  /**
   * transactions 배열을 10초 단위 버킷으로 집계.
   *
   * 예시 결과:
   *   [
   *     { time: "12:00:00", normal: 8, fraud: 2 },
   *     { time: "12:00:10", normal: 9, fraud: 1 },
   *     ...
   *   ]
   */
  const chartData = useMemo(() => {
    if (!transactions.length) return [];

    // 10초 단위로 그룹화
    const buckets = {};
    transactions.forEach(tx => {
      // timestamp를 10초 단위로 내림
      const sec = Math.floor((tx.timestamp || Date.now()) / 10000) * 10;
      const date = new Date(sec * 1000);
      const label = date.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

      if (!buckets[label]) buckets[label] = { time: label, normal: 0, fraud: 0 };
      tx.isFraud ? buckets[label].fraud++ : buckets[label].normal++;
    });

    // 시간순 정렬 후 최근 12개 버킷만 반환
    return Object.values(buckets)
      .sort((a, b) => a.time.localeCompare(b.time))
      .slice(-12);
  }, [transactions]);

  return (
    <div style={cardStyle}>
      <h3 style={titleStyle}>실시간 거래 추세  /  实时交易趋势</h3>

      {chartData.length < 2 ? (
        <p style={{ color: "#666", textAlign: "center", paddingTop: "60px", fontSize: "13px" }}>
          데이터 수집 중... (数据收集中...)
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
            <XAxis
              dataKey="time"
              tick={{ fill: "#94A3B8", fontSize: 10 }}
              interval="preserveStartEnd"
            />
            <YAxis tick={{ fill: "#94A3B8", fontSize: 10 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ background: "#1E2A45", border: "none", borderRadius: "8px", color: "#fff" }}
              formatter={(value, name) => [
                `${value}건`,
                name === "normal" ? "정상 / 正常" : "사기 / 欺诈"
              ]}
            />
            <Legend
              formatter={(value) => value === "normal" ? "정상 / 正常" : "사기 / 欺诈"}
              wrapperStyle={{ color: "#94A3B8", fontSize: "12px" }}
            />
            {/* 정상 거래 — 파란선 */}
            <Line
              type="monotone"
              dataKey="normal"
              stroke="#06B6D4"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
            {/* 사기 거래 — 빨간선 */}
            <Line
              type="monotone"
              dataKey="fraud"
              stroke="#EF4444"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

const cardStyle = {
  background: "#1a1a2e",
  borderRadius: "12px",
  padding: "20px",
  color: "white",
  flex: 1,
};

const titleStyle = {
  margin: "0 0 16px 0",
  fontSize: "15px",
  color: "#a0a0c0",
};
