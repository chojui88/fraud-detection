/**
 * FraudChart.jsx — 사기/정상 비율 파이 차트
 *
 * 작용：
 *   사기 거래와 정상 거래의 비율을 도넛 차트로 시각화한다.
 *
 * 用到的库：recharts
 *   recharts 是 React 生态里最流行的图表库，
 *   用起来像搭积木一样：PieChart 里放 Pie，Pie 里放 Cell（每个扇形）。
 */

import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

// 颜色定义
const COLORS = ['#ff4d4f', '#52c41a'];  // 红色=欺诈, 绿色=正常

export default function FraudChart({ stats }) {
  // recharts 需要的数据格式：[{ name, value }, ...]
  const data = [
    { name: '사기 거래', value: stats.fraudCount },
    { name: '정상 거래', value: stats.normalCount },
  ];

  // 数据都是0时，显示占位图
  if (stats.total === 0) {
    return (
      <div style={cardStyle}>
        <h3 style={titleStyle}>거래 분포</h3>
        <p style={{ color: '#888', textAlign: 'center', marginTop: '60px' }}>
          데이터 수집 중...
        </p>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      <h3 style={titleStyle}>거래 분포</h3>
      <PieChart width={300} height={280}>
        <Pie
          data={data}
          cx={150}        // 중심 X 좌표
          cy={130}        // 중심 Y 좌표
          innerRadius={70}  // 도넛 구멍 크기
          outerRadius={110} // 바깥 반지름
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value, name) => [`${value.toLocaleString()}건`, name]}
        />
        <Legend />
      </PieChart>
    </div>
  );
}

const cardStyle = {
  background: '#1a1a2e',
  borderRadius: '12px',
  padding: '20px',
  color: 'white',
};

const titleStyle = {
  margin: '0 0 16px 0',
  fontSize: '16px',
  color: '#a0a0c0',
};
