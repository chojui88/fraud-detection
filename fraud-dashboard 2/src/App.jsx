/**
 * App.jsx — 메인 앱 컴포넌트
 *
 * 개선 사항:
 *   1. TrendChart 추가 — 실시간 거래량 추세 꺾은선 그래프
 *   2. FraudAlert 추가 — 사기 감지 시 우측 하단 팝업 알림
 */

import { useState, useEffect, useRef } from 'react';
import StatsCards from './components/StatsCards';
import FraudChart from './components/FraudChart';
import TrendChart from './components/TrendChart';
import TransactionTable from './components/TransactionTable';
import FraudAlert from './components/FraudAlert';
import { fetchTransactions, fetchStats } from './api';

const DEFAULT_STATS = { total: 0, fraudCount: 0, normalCount: 0, fraudRate: 0 };

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats]               = useState(DEFAULT_STATS);
  const [lastUpdate, setLastUpdate]     = useState(null);
  const [isConnected, setIsConnected]   = useState(false);
  const [alerts, setAlerts]             = useState([]);  // 팝업 알림 목록

  // 이미 알림을 띄운 사기 거래 ID 기억 (중복 알림 방지)
  const seenFraudIds = useRef(new Set());

  // ─── 데이터 갱신 ──────────────────────────────────────────────────────────
  async function loadData() {
    try {
      const [txData, statsData] = await Promise.all([
        fetchTransactions(100),
        fetchStats(),
      ]);

      setTransactions(txData);
      setStats(statsData);
      setIsConnected(true);
      setLastUpdate(new Date().toLocaleTimeString());

      // ── 새로운 사기 거래 → 팝업 생성 ─────────────────────────────────────
      const newFrauds = txData.filter(
        tx => tx.isFraud && !seenFraudIds.current.has(tx.transactionId)
      );

      if (newFrauds.length > 0) {
        const newAlerts = newFrauds.slice(0, 3).map(tx => ({
          id: tx.transactionId + Date.now(),
          transactionId: tx.transactionId,
          amount: tx.amount,
          freqScore: tx.freqScore || 0,
        }));

        setAlerts(prev => [...prev, ...newAlerts]);
        newFrauds.forEach(tx => seenFraudIds.current.add(tx.transactionId));

        // 3초 후 자동 제거
        setTimeout(() => {
          setAlerts(prev =>
            prev.filter(a => !newAlerts.find(na => na.id === a.id))
          );
        }, 3000);
      }

    } catch (err) {
      setIsConnected(false);
    }
  }

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  function dismissAlert(id) {
    setAlerts(prev => prev.filter(a => a.id !== id));
  }

  // ─── UI ───────────────────────────────────────────────────────────────────
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f0f1a',
      padding: '24px',
      fontFamily: 'system-ui, sans-serif',
    }}>
      {/* 헤더 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ color: 'white', margin: 0, fontSize: '22px' }}>
            🔍 결제 사기 탐지 대시보드  /  支付欺诈检测仪表盘
          </h1>
          <p style={{ color: '#666', margin: '4px 0 0 0', fontSize: '13px' }}>
            실시간 모니터링 · Random Forest (5特征) · 고빈도 거래 감지
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: isConnected ? '#22C55E' : '#EF4444',
            display: 'inline-block',
          }} />
          <span style={{ color: '#888', fontSize: '13px' }}>
            {isConnected ? `연결됨 · ${lastUpdate}` : '백엔드 미연결 / 后端未连接'}
          </span>
        </div>
      </div>

      {/* 통계 카드 */}
      <StatsCards stats={stats} />

      {/* 차트 행: 파이차트 + 추세 꺾은선 */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        <div style={{ flexShrink: 0 }}>
          <FraudChart stats={stats} />
        </div>
        <TrendChart transactions={transactions} />
      </div>

      {/* 거래 테이블 */}
      <TransactionTable transactions={transactions} />

      {/* 사기 감지 팝업 알림 */}
      <FraudAlert alerts={alerts} onDismiss={dismissAlert} />
    </div>
  );
}
