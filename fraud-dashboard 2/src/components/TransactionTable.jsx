/**
 * TransactionTable.jsx — 실시간 거래 목록 테이블
 *
 * 작용：
 *   최근 거래 내역을 테이블로 보여준다.
 *   사기 거래는 빨간색, 정상 거래는 초록색으로 강조 표시한다.
 *
 * props:
 *   transactions — App에서 전달되는 거래 배열
 */

export default function TransactionTable({ transactions }) {
  return (
    <div style={cardStyle}>
      <h3 style={titleStyle}>실시간 거래 내역</h3>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ color: '#a0a0c0', borderBottom: '1px solid #333' }}>
              <th style={thStyle}>상태</th>
              <th style={thStyle}>거래ID</th>
              <th style={thStyle}>유저ID</th>
              <th style={thStyle}>금액</th>
              <th style={thStyle}>계좌번호</th>
              <th style={thStyle}>IP</th>
              <th style={thStyle}>기기</th>
              <th style={thStyle}>이상 점수</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                  데이터 수집 중... (Kafka 연결 확인)
                </td>
              </tr>
            ) : (
              transactions.map((tx, i) => (
                <tr
                  key={tx.transactionId + i}
                  style={{
                    borderBottom: '1px solid #222',
                    background: tx.isFraud ? 'rgba(255,77,79,0.08)' : 'transparent',
                  }}
                >
                  {/* 상태 뱃지 */}
                  <td style={tdStyle}>
                    <span style={{
                      background: tx.isFraud ? '#5f1e1e' : '#1e5f2a',
                      color: tx.isFraud ? '#ff4d4f' : '#52c41a',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 'bold',
                    }}>
                      {tx.isFraud ? '🚨 사기' : '✅ 정상'}
                    </span>
                  </td>
                  <td style={{ ...tdStyle, fontFamily: 'monospace', color: '#aaa' }}>
                    {tx.transactionId}
                  </td>
                  <td style={tdStyle}>{tx.userId}</td>
                  <td style={{ ...tdStyle, fontWeight: 'bold', color: tx.isFraud ? '#ff4d4f' : 'white' }}>
                    {tx.amount?.toLocaleString()}원
                  </td>
                  <td style={{ ...tdStyle, color: '#aaa' }}>{tx.accountNo}</td>
                  <td style={{ ...tdStyle, color: '#aaa' }}>{tx.ipAddress}</td>
                  <td style={{ ...tdStyle, color: '#aaa' }}>{tx.deviceId}</td>
                  <td style={{ ...tdStyle, color: tx.anomalyScore < 0 ? '#ff4d4f' : '#52c41a' }}>
                    {tx.anomalyScore}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
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

const thStyle = {
  textAlign: 'left',
  padding: '8px 12px',
  fontWeight: 'normal',
};

const tdStyle = {
  padding: '10px 12px',
  color: 'white',
};
