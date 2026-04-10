import React from 'react';
import { AdvancedRealTimeChart } from "react-ts-tradingview-widgets";

const TradingChart = ({ data }) => {
  // If we don't have ML data loaded yet, show loading
  if (!data || data.length === 0) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <div className="live-dot" style={{ marginRight: '10px' }} />
        Loading simulation data...
      </div>
    );
  }

  // Calculate ML Metrics to display above the TradingView chart
  const totalTrades = data.length;
  const winningTrades = data.filter(d => (d.pnl || 0) > 0).length;
  const winRate = totalTrades > 0 ? ((winningTrades / totalTrades) * 100).toFixed(1) : '0.0';
  const currentCumPnl = data[data.length - 1].cumPnl;

  return (
    <div style={{ width: '100%', height: 'calc(100% - 20px)', display: 'flex', flexDirection: 'column' }}>
      
      {/* Analytics Overlay Bar for ML Data */}
      <div className="analytics-bar">
        <div className="metric-card">
          <span className="metric-label">ML Total Ticks</span>
          <span className="metric-value">{totalTrades}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">ML Win Rate</span>
          <span className="metric-value">{winRate}%</span>
        </div>
        <div className="metric-card" style={{ borderRight: 'none' }}>
          <span className="metric-label">Local Net PnL</span>
          <span className={`metric-value ${currentCumPnl >= 0 ? 'buy' : 'sell'}`}>
            {currentCumPnl >= 0 ? '+' : ''}{currentCumPnl.toFixed(2)}
          </span>
        </div>
        
        {/* Helper text about the integration limitation */}
        <div style={{ marginLeft: 'auto', alignSelf: 'center', background: 'var(--bg-panel-hover)', padding: '8px 12px', borderRadius: '8px', fontSize: '0.85rem', color: 'var(--text-muted)', border: '1px solid rgba(255,255,255,0.05)', maxWidth: '300px' }}>
          <span style={{color: 'var(--buy-color)'}}>Note:</span> This is the full TradingView widget. It uses live market data. Local custom ML indicators (data.csv) are displayed in the feed/metrics panels.
        </div>
      </div>

      {/* Full TradingView Advanced Chart Widget */}
      <div style={{ flex: 1, minHeight: '500px', width: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
        <AdvancedRealTimeChart 
          theme="dark" 
          autosize={true}
          symbol="BSE:RELIANCE" 
          interval="60"
          timezone="Asia/Kolkata"
          allow_symbol_change={true}
          details={true}
          hotlist={true}
          calendar={false}
          studies={[
            "MACD@tv-basicstudies",
            "MOM@tv-basicstudies"
          ]}
        />
      </div>

    </div>
  );
};

export default TradingChart;
