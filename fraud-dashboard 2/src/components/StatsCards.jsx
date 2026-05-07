/**
 * StatsCards.jsx — 상단 통계 카드 컴포넌트
 *
 * 작용：
 *   총 거래 수, 사기 건수, 정상 건수, 사기율을 카드 형태로 표시한다.
 *
 * 什么是 React 组件？
 *   组件就是一块可复用的 UI 片段。
 *   这里的 StatsCards 就是页面顶部那4个统计卡片。
 *   父组件（App）把数据（stats）传给它，它负责渲染成 HTML。
 *
 * props（属性）：
 *   stats — 从 App 传入的统计数据对象
 */

export default function StatsCards({ stats }) {
  // 定义4张卡片的内容
  const cards = [
    {
      label: '총 거래 수',
      value: stats.total.toLocaleString(),  // 숫자에 쉼표 추가 (예: 1,234)
      bg: '#1e3a5f',
      icon: '💳',
    },
    {
      label: '사기 거래',
      value: stats.fraudCount.toLocaleString(),
      bg: '#5f1e1e',
      icon: '🚨',
    },
    {
      label: '정상 거래',
      value: stats.normalCount.toLocaleString(),
      bg: '#1e5f2a',
      icon: '✅',
    },
    {
      label: '사기율',
      value: `${stats.fraudRate}%`,
      bg: stats.fraudRate > 10 ? '#5f3a1e' : '#2a1e5f',  // 10% 초과시 주황색
      icon: '📊',
    },
  ];

  return (
    <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            flex: 1,
            background: card.bg,
            borderRadius: '12px',
            padding: '20px',
            color: 'white',
          }}
        >
          <div style={{ fontSize: '28px' }}>{card.icon}</div>
          <div style={{ fontSize: '13px', opacity: 0.8, marginTop: '8px' }}>{card.label}</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', marginTop: '4px' }}>{card.value}</div>
        </div>
      ))}
    </div>
  );
}
