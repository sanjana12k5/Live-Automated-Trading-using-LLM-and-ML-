import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <div style={{ fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
          Tick: <span style={{ color: '#fff' }}>{data.id}</span>
        </div>
        <div style={{ marginBottom: '12px', fontSize: '1.05rem', fontWeight: 500 }}>
          {data.pattern}
        </div>
        <div style={{
          display: 'flex', 
          flexDirection: 'column',
          gap: '6px',
          paddingTop: '8px',
          borderTop: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Net PnL</span>
            <span style={{
              color: data.cumPnl >= 0 ? 'var(--buy-color)' : 'var(--sell-color)',
              fontWeight: 'bold',
              textShadow: data.cumPnl >= 0 ? '0 0 10px rgba(0,255,163,0.4)' : '0 0 10px rgba(255,51,102,0.4)'
            }}>
              {data.cumPnl >= 0 ? '+' : ''}{data.cumPnl.toFixed(2)}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Trade PnL</span>
            <span style={{
              color: data.pnl >= 0 ? 'var(--buy-color)' : 'var(--sell-color)',
              fontWeight: 'bold'
            }}>
              {data.pnl >= 0 ? '+' : ''}{(data.pnl || 0).toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

const TradingChart = ({ data }) => {
  const [chartMode, setChartMode] = useState('cumulative'); // 'cumulative' | 'individual'

  if (!data || data.length === 0) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <div className="live-dot" style={{ marginRight: '10px' }} />
        Loading simulation data...
      </div>
    );
  }

  // Calculate Metrics real-time
  const totalTrades = data.length;
  // filter by signal type not completely relevant if pnl reflects the outcome
  // Assuming a win is pnl > 0
  const winningTrades = data.filter(d => (d.pnl || 0) > 0).length;
  const winRate = totalTrades > 0 ? ((winningTrades / totalTrades) * 100).toFixed(1) : '0.0';
  
  const currentCumPnl = data[data.length - 1].cumPnl;

  const pnlValues = data.map(d => d.cumPnl);
  const minPnl = Math.min(0, ...pnlValues);
  const maxPnl = Math.max(0, ...pnlValues);
  const padding = (maxPnl - minPnl) * 0.1 || 1;

  // For Bar Chart individual pnl
  const indPnlValues = data.map(d => d.pnl || 0);
  const minInd = Math.min(0, ...indPnlValues);
  const maxInd = Math.max(0, ...indPnlValues);
  const paddingInd = (maxInd - minInd) * 0.1 || 1;

  return (
    <div style={{ width: '100%', height: 'calc(100% - 60px)', display: 'flex', flexDirection: 'column' }}>

      {/* Analytics Overlay Bar */}
      <div className="analytics-bar">
        <div className="metric-card">
          <span className="metric-label">Total Trades</span>
          <span className="metric-value">{totalTrades}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Win Rate</span>
          <span className="metric-value">{winRate}%</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Gross PnL</span>
          <span className={`metric-value ${currentCumPnl >= 0 ? 'buy' : 'sell'}`}>
            {currentCumPnl >= 0 ? '+' : ''}{currentCumPnl.toFixed(2)}
          </span>
        </div>

        <div style={{ marginLeft: 'auto', alignSelf: 'center' }}>
          <div className="chart-toggles">
            <button 
              className={`toggle-btn ${chartMode === 'cumulative' ? 'active' : ''}`}
              onClick={() => setChartMode('cumulative')}
            >
              Equity Curve
            </button>
            <button 
              className={`toggle-btn ${chartMode === 'individual' ? 'active' : ''}`}
              onClick={() => setChartMode('individual')}
            >
              Trade PnL
            </button>
          </div>
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartMode === 'cumulative' ? (
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent-color)" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="var(--accent-color)" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorPnlStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#fff" />
                  <stop offset="100%" stopColor="var(--accent-color)" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="id" 
                stroke="var(--text-muted)" 
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                tickLine={{ stroke: 'transparent' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                minTickGap={40}
              />
              <YAxis 
                domain={[minPnl - padding, maxPnl + padding]} 
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                tickLine={{ stroke: 'transparent' }}
                axisLine={{ stroke: 'transparent' }}
                tickFormatter={(value) => value.toFixed(1)}
                orientation="right"
              />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1, strokeDasharray: '5 5' }} />
              <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
              <Area
                type="monotone"
                dataKey="cumPnl"
                stroke="url(#colorPnlStroke)"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorPnl)"
                activeDot={{ r: 6, fill: '#fff', stroke: 'var(--accent-color)', strokeWidth: 3, style: { filter: 'drop-shadow(0px 0px 8px var(--accent-glow))' } }}
                isAnimationActive={false}
              />
            </AreaChart>
          ) : (
            <BarChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="id" 
                stroke="var(--text-muted)" 
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                tickLine={{ stroke: 'transparent' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                minTickGap={40}
              />
              <YAxis 
                domain={[minInd - paddingInd, maxInd + paddingInd]} 
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                tickLine={{ stroke: 'transparent' }}
                axisLine={{ stroke: 'transparent' }}
                tickFormatter={(value) => value.toFixed(2)}
                orientation="right"
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
              <Bar dataKey="pnl" isAnimationActive={false}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={(entry.pnl || 0) >= 0 ? 'var(--buy-color)' : 'var(--sell-color)'} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default TradingChart;
