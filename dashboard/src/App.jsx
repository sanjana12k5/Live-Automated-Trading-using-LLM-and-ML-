import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import TradingChart from './components/TradingChart';
import SuggestionsFeed from './components/SuggestionsFeed';
import { Activity } from 'lucide-react';

function App() {
  const [data, setData] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    // Load CSV data
    const loadData = async () => {
      try {
        const response = await fetch('/data.csv');
        const csvText = await response.text();
        
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: (results) => {
            // Add cumulative PnL to each row to draw the chart smoothly
            let cumPnl = 0;
            const parsedData = results.data.map((row, index) => {
              cumPnl += (row.pnl || 0);
              return {
                ...row,
                id: index, // unique id for animation
                cumPnl: cumPnl,
              };
            });
            setData(parsedData);
            setCurrentIndex(Math.min(50, parsedData.length)); // Start with some initial data
          }
        });
      } catch (error) {
        console.error("Error loading CSV: ", error);
      }
    };
    
    loadData();
  }, []);

  // Simulation logic
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
      }, 500); // add one new tick every 500ms
    }
    return () => clearInterval(interval);
  }, [isSimulating, currentIndex, data.length]);

  const visibleData = data.slice(0, currentIndex);
  // Get recent suggestions (last 20 for the feed, reverse to put newest on top)
  const recentSuggestions = [...visibleData].reverse().slice(0, 20);

  return (
    <div className="dashboard-container">
      <div className="panel chart-panel">
        <div className="panel-header">
          <h2 className="panel-title">
            <Activity size={24} color="var(--accent-color)" />
            Simulation Performance
          </h2>
          <button 
            className="suggestion-badge" 
            style={{ 
              cursor: 'pointer', 
              background: isSimulating ? 'rgba(255,61,0,0.1)' : 'rgba(0,230,118,0.1)', 
              color: isSimulating ? 'var(--sell-color)' : 'var(--buy-color)',
              border: '1px solid transparent'
            }}
            onClick={() => setIsSimulating(!isSimulating)}
          >
            {isSimulating ? 'Pause Simulation' : 'Start Simulation'}
          </button>
        </div>
        <TradingChart data={visibleData} />
      </div>
      
      <div className="panel feed-panel">
        <div className="panel-header">
          <h2 className="panel-title">Live Suggestions</h2>
          <span style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{currentIndex} / {data.length}</span>
        </div>
        <SuggestionsFeed suggestions={recentSuggestions} />
      </div>
    </div>
  );
}

export default App;
