import React from 'react';
import { History, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const ExecutionLog = ({ trades }) => {
  return (
    <div className="panel execution-panel" style={{ flex: 1, marginTop: '1.5rem', overflowY: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div className="panel-header" style={{ marginBottom: '0.5rem' }}>
        <h2 className="panel-title">
          <History size={20} color="var(--accent-color)" />
          Execution Log
        </h2>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '12px' }}>
          {trades.length} trades
        </span>
      </div>

      <div className="table-container" style={{ overflowY: 'auto', flex: 1 }}>
        <table className="execution-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Type</th>
              <th>Price</th>
              <th>Size</th>
              <th>PnL</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  No trades executed yet.
                </td>
              </tr>
            ) : (
              [...trades].reverse().map((trade, i) => {
                const isBuy = trade.type.toUpperCase() === 'LONG';
                const pnl = trade.pnl || 0;
                return (
                  <tr key={i} className="trade-row">
                    <td>{trade.time}</td>
                    <td>
                      <span className={`trade-badge ${isBuy ? 'buy' : 'sell'}`}>
                        {isBuy ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />} {trade.type}
                      </span>
                    </td>
                    <td>${trade.price}</td>
                    <td>${trade.size}</td>
                    <td className={`pnl-val ${pnl > 0 ? 'pnl-positive' : pnl < 0 ? 'pnl-negative' : ''}`}>
                      {pnl > 0 ? '+' : ''}{pnl.toFixed(2)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExecutionLog;
