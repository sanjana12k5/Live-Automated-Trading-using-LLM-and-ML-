import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
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
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          paddingTop: '8px',
          borderTop: '1px solid rgba(255,255,255,0.1)'
        }}>
          <span style={{ color: 'var(--text-muted)' }}>PnL</span>
          <span style={{
            color: data.cumPnl >= 0 ? 'var(--buy-color)' : 'var(--sell-color)',
            fontWeight: 'bold',
            fontSize: '1.1rem',
            textShadow: data.cumPnl >= 0 ? '0 0 10px rgba(0,255,163,0.4)' : '0 0 10px rgba(255,51,102,0.4)'
          }}>
            {data.cumPnl >= 0 ? '+' : ''}{data.cumPnl.toFixed(2)}
          </span>
        </div>
      </div>
    );
  }
  return null;
};

const TradingChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <div className="live-dot" style={{ marginRight: '10px' }} />
        Loading simulation data...
      </div>
    );
  }

  const pnlValues = data.map(d => d.cumPnl);
  const minPnl = Math.min(0, ...pnlValues);
  const maxPnl = Math.max(0, ...pnlValues);
  const padding = (maxPnl - minPnl) * 0.1 || 1;

  // Render a seamless gradient for the cumulative PnL area chart
  return (
    <div style={{ width: '100%', height: 'calc(100% - 60px)' }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 20, right: 30, left: 10, bottom: 0 }}
        >
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
      </ResponsiveContainer>
    </div>
  );
};

export default TradingChart;
