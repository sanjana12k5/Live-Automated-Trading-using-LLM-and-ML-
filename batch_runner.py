
import pandas as pd
from simulator.live_simulator import run_live_simulation

def run_batch():
    all_trades = []
    
    print("Starting Batch Simulation (20 Runs)...")
    
    for i in range(5):
        print(f"  Run {i+1}/5...", end="\r")
        portfolio = run_live_simulation(candles=350, start_price=100.0, symbol=f"SIM-{i}", enable_plot=False)
        
        for trade in portfolio.trade_log:
            all_trades.append({
                "run": i,
                "pattern": trade.get("pattern"),
                "signal": trade.get("signal"),
                "score": trade.get("score"),
                "ml_prob": trade.get("ml_prob"),
                "pnl": trade.get("pnl"),
                "reason": trade.get("reason")
            })
            
    # Create DataFrame
    df = pd.DataFrame(all_trades)
    df.to_csv("simulation_results.csv", index=False)
    print(f"\nBatch Run Complete. Saved {len(df)} trades to simulation_results.csv")

if __name__ == "__main__":
    run_batch()
