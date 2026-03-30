
import pandas as pd
import numpy as np

def analyze():
    print("Loading simulation_results.csv...")
    try:
        df = pd.read_csv("simulation_results.csv")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    patterns = df["pattern"].unique()
    print(f"Found {len(patterns)} patterns: {patterns}")
    
    best_config = {}
    
    # Grid Search Settings
    score_thresholds = np.arange(0.40, 0.75, 0.05)
    ml_thresholds = np.arange(0.10, 0.60, 0.05)
    
    print("\nOptimizing Thresholds per Pattern...")
    print("-" * 60)
    print(f"{'Pattern':<20} | {'Cfg(Scr/ML)':<12} | {'Trades':<6} | {'PnL':<8} | {'Win%':<6}")
    print("-" * 60)
    
    total_opt_pnl = 0.0
    
    for pat in patterns:
        pat_df = df[df["pattern"] == pat]
        
        best_pnl = -9999
        best_params = (0.50, 0.50) # default
        best_count = 0
        best_wr = 0.0
        
        # Brute force search for best PnL
        valid_configs = []
        
        for s in score_thresholds:
            for m in ml_thresholds:
                # Filter trades
                subset = pat_df[
                    (pat_df["score"] >= s) & 
                    (pat_df["ml_prob"] >= m)
                ]
                
                if len(subset) == 0:
                    continue
                    
                pnl = subset["pnl"].sum()
                
                # Relaxed constraints for Volume search:
                # At least 2 trades, PnL > 0
                if len(subset) >= 2 and pnl > 0:
                     wr = (len(subset[subset["pnl"] > 0]) / len(subset)) * 100
                     valid_configs.append({
                         "score": s, 
                         "ml": m, 
                         "pnl": pnl, 
                         "count": len(subset), 
                         "wr": wr
                     })

        # Sort by PnL descending
        valid_configs.sort(key=lambda x: x["pnl"], reverse=True)
        
        print(f"\n[{pat}]")
        if not valid_configs:
            print("  No profitable config found.")
            best_config[pat] = (0.65, 0.55) # Default defensive
        else:
            # Pick top 1 for config dict, but print top 3 for info
            best = valid_configs[0]
            best_config[pat] = (best["score"], best["ml"])
            
            for i, c in enumerate(valid_configs[:3]):
                print(f"  #{i+1}: S={c['score']:.2f}/M={c['ml']:.2f} | Count={c['count']} | PnL=${c['pnl']:.2f} | WR={c['wr']:.1f}%")


    print("-" * 60)
    print("Optimization Complete.")
    print("Recommended Configuration Dict:")
    print("PATTERN_CONFIG = {")
    for pat, params in best_config.items():
        print(f'    "{pat}": {{ "thresh": {params[0]:.2f}, "min_ml": {params[1]:.2f} }},')
    print("}")

if __name__ == "__main__":
    analyze()
