import React from 'react';
import { TrendingUp, TrendingDown, Target } from 'lucide-react';

const SuggestionsFeed = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '3rem', fontStyle: 'italic' }}>
        <div className="live-dot" style={{ display: 'inline-block', marginRight: '8px', opacity: 0.5 }}></div>
        Waiting for signals...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', paddingTop: '0.5rem' }}>
      {suggestions.map((item, index) => {
        const isBuy = item.signal.toUpperCase() === 'BUY';
        const scorePct = Math.round((item.score || 0) * 100);
        
        // Add a simple animation class only to the newest item if it just arrived
        const isNewest = index === 0;

        return (
          <div key={`${item.id}-${index}`} className={`suggestion-card type-${isBuy ? 'buy' : 'sell'} ${isNewest ? 'new-item' : ''}`}>
            
            <div className="suggestion-header">
              <span className={`suggestion-badge ${isBuy ? 'buy' : 'sell'}`}>
                {item.signal}
              </span>
              <span style={{ 
                fontSize: '0.85rem', 
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(0,0,0,0.2)',
                padding: '4px 8px',
                borderRadius: '8px'
              }}>
                <Target size={14} /> ID: {item.id}
              </span>
            </div>
            
            <div className="suggestion-pattern" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ 
                background: isBuy ? 'rgba(0,255,163,0.1)' : 'rgba(255,51,102,0.1)',
                padding: '8px', 
                borderRadius: '50%',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                boxShadow: isBuy ? '0 0 10px rgba(0,255,163,0.2)' : '0 0 10px rgba(255,51,102,0.2)'
              }}>
                {isBuy ? <TrendingUp size={20} color="var(--buy-color)" /> : <TrendingDown size={20} color="var(--sell-color)" />}
              </div>
              {item.pattern}
            </div>
            
            <div className="suggestion-details">
              <span style={{ letterSpacing: '0.5px' }}>Confidence Score</span>
              <span style={{ fontWeight: 700, color: '#fff', fontSize: '1.05rem', textShadow: '0 0 5px rgba(255,255,255,0.3)' }}>
                {scorePct}%
              </span>
            </div>
            
            <div className="score-bar-bg">
              <div 
                className={`score-bar-fill ${isBuy ? 'buy' : 'sell'}`}
                style={{ width: `${scorePct}%` }}
              />
            </div>

          </div>
        );
      })}
    </div>
  );
};

export default SuggestionsFeed;
