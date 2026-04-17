import React from 'react';
import { Settings, ShieldAlert, DollarSign, Target, Activity } from 'lucide-react';

const ConfigurationPanel = ({ config, setConfig, isAutoTrading, setIsAutoTrading }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="panel config-panel">
      <div className="panel-header">
        <h2 className="panel-title">
          <Settings size={20} color="var(--accent-color)" />
          Strategy Settings
        </h2>
      </div>

      <div className="config-form">
        <div className="form-group">
          <label><Activity size={14} /> Strategy Model</label>
          <select name="strategy" value={config.strategy} onChange={handleChange} className="form-control">
            <option value="ml_pattern">ML Pattern Recognition</option>
            <option value="ema_crossover">EMA Crossover (9, 15)</option>
            <option value="combined">Combined ML + EMA</option>
          </select>
        </div>

        <div className="form-group">
          <label><Target size={14} /> Confidence Threshold</label>
          <div className="slider-container">
            <input 
              type="range" 
              name="threshold" 
              min="0.5" 
              max="0.99" 
              step="0.01" 
              value={config.threshold} 
              onChange={handleChange} 
            />
            <span className="slider-value">{(config.threshold * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="form-group">
          <label><DollarSign size={14} /> Trade Size ($)</label>
          <input 
            type="number" 
            name="tradeSize" 
            value={config.tradeSize} 
            onChange={handleChange} 
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label><ShieldAlert size={14} /> Stop Loss (%)</label>
          <input 
            type="number" 
            name="stopLoss" 
            step="0.1" 
            value={config.stopLoss} 
            onChange={handleChange} 
            className="form-control"
          />
        </div>

        <div className="auto-trade-toggle-container">
          <div className="toggle-label">
            <h3 style={{margin:0, fontSize: '1rem', color: '#fff'}}>Automated Execution</h3>
            <p style={{margin:0, fontSize: '0.8rem', color: 'var(--text-muted)'}}>Enable bot to place live trades</p>
          </div>
          <label className="switch">
            <input type="checkbox" checked={isAutoTrading} onChange={(e) => setIsAutoTrading(e.target.checked)} />
            <span className="slider round"></span>
          </label>
        </div>
        
      </div>
    </div>
  );
};

export default ConfigurationPanel;
