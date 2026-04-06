import React from 'react';
import { TrendingUp, TrendingDown, Target } from 'lucide-react';

const SuggestionsFeed = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>
        Waiting for signals...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {suggestions.map((item, index) => {
        const isBuy = item.signal.toUpperCase() === 'BUY';
        const scorePct = Math.round((item.score || 0) * 100);
        
        // Add a simple animation class only to the newest item if it just arrived
        const isNewest = index === 0;

        return (
          <div key={`${item.id}-${index}`} className={`suggestion-card ${isNewest ? 'new-item' : ''}`}>
            <div className="suggestion-header">
              <span className={`suggestion-badge ${isBuy ? 'buy' : 'sell'}`}>
                {item.signal}
              </span>
              <span style={{ 
                fontSize: '0.85rem', 
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <Target size={14} /> ID: {item.id}
              </span>
            </div>
            
            <div className="suggestion-pattern" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {isBuy ? <TrendingUp size={18} color="var(--buy-color)" /> : <TrendingDown size={18} color="var(--sell-color)" />}
              {item.pattern}
            </div>
            
            <div className="suggestion-details">
              <span>Confidence Score</span>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{scorePct}%</span>
            </div>
            
            <div className="score-bar-bg">
              <div 
                className="score-bar-fill" 
                style={{ 
                  width: `${scorePct}%`,
                  backgroundColor: isBuy ? 'var(--buy-color)' : 'var(--sell-color)'
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SuggestionsFeed;
