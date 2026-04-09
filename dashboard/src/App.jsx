import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import TradingChart from './components/TradingChart';
import SuggestionsFeed from './components/SuggestionsFeed';
import { Activity, Zap } from 'lucide-react';

function App() {
  const [data, setData] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch('/data.csv');
        const csvText = await response.text();
        
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: (results) => {
            let cumPnl = 0;
            const parsedData = results.data.map((row, index) => {
              cumPnl += (row.pnl || 0);
              return {
                ...row,
                id: index,
                cumPnl: cumPnl,
              };
            });
            setData(parsedData);
            setCurrentIndex(Math.min(50, parsedData.length));
          }
        });
      } catch (error) {
        console.error("Error loading CSV: ", error);
      }
    };
    
    loadData();
  }, []);

  useEffect(() => {
    let interval;
    if (isSimulating && currentIndex < data.length) {
      interval = setInterval(() => {
        setCurrentIndex(prev => {
          if (prev >= data.length - 1) {
            setIsSimulating(false);
            return prev;
          }
          return prev + 1;
        });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isSimulating, currentIndex, data.length]);

  const visibleData = data.slice(0, currentIndex);
  const recentSuggestions = [...visibleData].reverse().slice(0, 20);

  return (
    <>
      <header className="app-header">
        <h1 className="app-title">
          <Zap size={28} color="var(--accent-color)" fill="var(--accent-color)" style={{ filter: 'drop-shadow(0 0 10px var(--accent-glow))' }} />
          Nexus Trade
        </h1>
        
        {isSimulating && (
          <div className="live-indicator">
            <div className="live-dot"></div>
            LIVE
          </div>
        )}
      </header>

      <div className="dashboard-container">
        <main className="panel chart-panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Activity size={24} color="var(--accent-color)" />
              Simulation Performance
            </h2>
            <button 
              className={`suggestion-badge ${isSimulating ? 'sell' : 'buy'}`} 
              style={{ cursor: 'pointer', outline: 'none' }}
              onClick={() => setIsSimulating(!isSimulating)}
            >
              {isSimulating ? 'Pause Simulation' : 'Start Simulation'}
            </button>
          </div>
          <TradingChart data={visibleData} />
        </main>
        
        <aside className="panel feed-panel">
          <div className="panel-header" style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-panel)', zIndex: 10, paddingBottom: '0.5rem', backdropFilter: 'blur(10px)' }}>
            <h2 className="panel-title">Signal Feed</h2>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '12px' }}>
              Tick {currentIndex} / {data.length}
            </span>
          </div>
          <SuggestionsFeed suggestions={recentSuggestions} />
        </aside>
      </div>
    </>
  );
}

export default App;
