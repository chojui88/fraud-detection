/**
 * FraudAlert.jsx — 欺诈警报弹窗
 *
 * 作用：
 *   새로운 사기 거래가 감지되면 화면 우측 하단에 빨간 알림이 튀어나옴.
 *   3초 후 자동으로 사라짐.
 *
 * props:
 *   alerts — App.jsx에서 전달하는 알림 배열
 *            [{ id, transactionId, amount, freqScore }, ...]
 *   onDismiss — 알림 닫기 콜백
 */

export default function FraudAlert({ alerts, onDismiss }) {
  if (!alerts.length) return null;

  return (
    <div style={containerStyle}>
      {alerts.map(alert => (
        <div key={alert.id} style={alertStyle}>
          {/* 왼쪽 빨간 강조 바 */}
          <div style={accentBar} />

          <div style={{ flex: 1 }}>
            {/* 헤더 */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ color: "#EF4444", fontWeight: "bold", fontSize: "13px" }}>
                🚨 사기 거래 감지  /  检测到欺诈交易
              </span>
              <button
                onClick={() => onDismiss(alert.id)}
                style={closeBtn}
              >
                ✕
              </button>
            </div>

            {/* 거래 정보 */}
            <div style={{ marginTop: "6px", fontSize: "12px", color: "#CBD5E1" }}>
              <span style={{ color: "#94A3B8" }}>거래ID: </span>
              <span style={{ fontFamily: "monospace" }}>{alert.transactionId}</span>
            </div>
            <div style={{ fontSize: "12px", color: "#CBD5E1" }}>
              <span style={{ color: "#94A3B8" }}>금액: </span>
              <span style={{ color: "#EF4444", fontWeight: "bold" }}>
                {alert.amount?.toLocaleString()}원
              </span>
              {alert.freqScore >= 5 && (
                <span style={{ marginLeft: "8px", color: "#F59E0B", fontSize: "11px" }}>
                  ⚡ 고빈도 거래 (高频交易 ×{alert.freqScore})
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── 스타일 ──────────────────────────────────────────────────────────────────

const containerStyle = {
  position: "fixed",
  bottom: "24px",
  right: "24px",
  zIndex: 1000,
  display: "flex",
  flexDirection: "column",
  gap: "10px",
  maxWidth: "340px",
};

const alertStyle = {
  background: "#1E2A45",
  border: "1px solid #EF4444",
  borderRadius: "10px",
  padding: "12px 14px",
  display: "flex",
  gap: "10px",
  boxShadow: "0 4px 20px rgba(239, 68, 68, 0.3)",
  animation: "slideIn 0.3s ease",
};

const accentBar = {
  width: "4px",
  borderRadius: "2px",
  background: "#EF4444",
  flexShrink: 0,
};

const closeBtn = {
  background: "none",
  border: "none",
  color: "#94A3B8",
  cursor: "pointer",
  fontSize: "13px",
  padding: "0",
  lineHeight: 1,
};
