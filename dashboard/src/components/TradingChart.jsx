import React from 'react';
import {
  LineChart,
  Line,
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
      <div className="suggestion-card" style={{margin: 0, minWidth: '150px'}}>
        <div style={{fontWeight: 600, marginBottom: '4px'}}>Tick: {data.id}</div>
        <div style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '8px'}}>
          Pattern: <span style={{color: 'var(--text-main)'}}>{data.pattern}</span>
        </div>
        <div style={{
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span>PnL:</span>
          <span style={{
            color: data.cumPnl >= 0 ? 'var(--buy-color)' : 'var(--sell-color)',
            fontWeight: 'bold'
          }}>
            {data.cumPnl.toFixed(2)}
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
        Loading simulation data...
      </div>
    );
  }

  // Calculate dynamic domain to keep the line nicely centered
  const pnlValues = data.map(d => d.cumPnl);
  const minPnl = Math.min(0, ...pnlValues);
  const maxPnl = Math.max(0, ...pnlValues);
  const padding = (maxPnl - minPnl) * 0.1 || 1;

  return (
    <div style={{ width: '100%', height: 'calc(100% - 60px)' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
          <XAxis 
            dataKey="id" 
            stroke="var(--text-muted)" 
            tick={{fill: 'var(--text-muted)'}}
            tickLine={{stroke: 'var(--border-color)'}}
            axisLine={{stroke: 'var(--border-color)'}}
            minTickGap={30}
          />
          <YAxis 
            domain={[minPnl - padding, maxPnl + padding]} 
            stroke="var(--text-muted)"
            tick={{fill: 'var(--text-muted)'}}
            tickLine={{stroke: 'var(--border-color)'}}
            axisLine={{stroke: 'var(--border-color)'}}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.2)" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="cumPnl"
            stroke="var(--accent-color)"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: 'var(--accent-color)', stroke: 'var(--bg-panel)', strokeWidth: 2 }}
            isAnimationActive={false} // Disable inner animation to let the ticks drive it
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TradingChart;
