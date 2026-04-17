import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import TradingChart from './components/TradingChart';
import SuggestionsFeed from './components/SuggestionsFeed';
import ConfigurationPanel from './components/ConfigurationPanel';
import ExecutionLog from './components/ExecutionLog';
import { Activity, Zap } from 'lucide-react';
import { generateMockOHLC } from './utils/MockDataGenerator';

function App() {
  const [data, setData] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isAutoTrading, setIsAutoTrading] = useState(false);
  
  const [config, setConfig] = useState({
    strategy: 'ml_pattern',
    threshold: 0.85,
    tradeSize: 1000,
    stopLoss: 2.5
  });

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
            // Generate full length OHLC data corresponding to the number of rows
            const mockCandles = generateMockOHLC(results.data.length, 150);

            const parsedData = results.data.map((row, index) => {
              cumPnl += (row.pnl || 0);
              return {
                ...row,
                id: index,
                cumPnl: cumPnl,
                time: mockCandles[index].time,
                open: mockCandles[index].open,
                high: mockCandles[index].high,
                low: mockCandles[index].low,
                close: mockCandles[index].close,
                value: mockCandles[index].close, // Provide value for line chart compatibility
                volume: mockCandles[index].volume,
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
  
  // Deriving execution logs from signals to simulate bot trading over the data
  // Using config.threshold to filter out trades if desired, for now just taking all signals
  const executedTrades = visibleData
    .filter(row => row.signal)
    .map(row => ({
      time: new Date(row.time).toLocaleTimeString(),
      type: row.signal.toUpperCase() === 'BUY' ? 'LONG' : 'SHORT',
      price: row.close || row.value,
      size: config.tradeSize,
      pnl: row.pnl
    }));

  return (
    <>
      <header className="app-header">
        <h1 className="app-title">
          <Zap size={28} color="var(--accent-color)" fill="var(--accent-color)" style={{ filter: 'drop-shadow(0 0 10px var(--accent-glow))' }} />
          Nexus Trade
        </h1>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {isAutoTrading && (
            <div className="active-trade-badge">
              Auto-Trade Active
            </div>
          )}
          {isSimulating && (
            <div className="live-indicator">
              <div className="live-dot"></div>
              LIVE
            </div>
          )}
        </div>
      </header>

      <div className="dashboard-container multi-col">
        {/* Left Sidebar: Settings */}
        <aside className="left-sidebar">
          <ConfigurationPanel 
            config={config} 
            setConfig={setConfig} 
            isAutoTrading={isAutoTrading} 
            setIsAutoTrading={setIsAutoTrading} 
          />
          {/* Portfolio Metrics can be added here or top bar */}
        </aside>

        {/* Center: Main Chart */}
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
        
        {/* Right Sidebar: Feeds & Logs */}
        <aside className="right-sidebar">
          <div className="panel feed-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'hidden' }}>
            <div className="panel-header" style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-panel)', zIndex: 10, paddingBottom: '0.5rem', backdropFilter: 'blur(10px)' }}>
              <h2 className="panel-title">Signal Feed</h2>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '12px' }}>
                Tick {currentIndex} / {data.length}
              </span>
            </div>
            <div style={{ overflowY: 'auto' }}>
              <SuggestionsFeed suggestions={recentSuggestions} />
            </div>
          </div>

          <ExecutionLog trades={executedTrades} />
        </aside>
      </div>
    </>
  );
}

export default App;
