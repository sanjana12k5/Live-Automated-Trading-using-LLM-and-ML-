import time
from simulator.live_simulator import run_live_simulation

def main():
    symbol = "AAPL"
    
    print("\n" + "="*50)
    print(" 🚀 RUNNING ANALYSIS 1: DEFAULT (ML + PATTERNS) ")
    print("="*50)
    
    start_time = time.time()
    # disable plotting manually to speed it up if it takes too long
    # Run the existing logic exactly as it is
    portfolio_default = run_live_simulation(
        symbol=symbol, 
        enable_plot=False, 
        strategy_mode="DEFAULT"
    )
    time_default = time.time() - start_time
    
    print("\n" + "="*50)
    print(" 🚀 RUNNING ANALYSIS 2: EMA_ONLY (9x15 CROSSOVER) ")
    print("="*50)
    
    start_time = time.time()
    portfolio_ema = run_live_simulation(
        symbol=symbol, 
        enable_plot=False, 
        strategy_mode="EMA_ONLY"
    )
    time_ema = time.time() - start_time

    print("\n" + "="*50)
    print(" 🚀 RUNNING ANALYSIS 3: COMBINED (PATTERNS + EMA CROSS) ")
    print("="*50)
    
    start_time = time.time()
    portfolio_combined = run_live_simulation(
        symbol=symbol, 
        enable_plot=False, 
        strategy_mode="COMBINED"
    )
    time_combined = time.time() - start_time

    print("\n" + "#"*70)
    print("                         FINAL COMPARISON                           ")
    print("#"*70)
    print(f"{'Metric':<15} | {'DEFAULT (ML+Pat)':<16} | {'EMA_ONLY':<15} | {'COMBINED':<15}")
    print("-" * 70)
    
    # helper for metrics
    def get_metrics(port):
        wins = [t for t in port.trade_log if t["pnl"] > 0]
        win_rate = (len(wins) / len(port.trade_log)) * 100 if port.trade_log else 0
        total_pnl = port.cash - 100000
        total_trades = len(port.trade_log)
        return f"${total_pnl:,.2f}", f"{total_trades}", f"{win_rate:.1f}%"
        
    def_pnl, def_trades, def_wr = get_metrics(portfolio_default)
    ema_pnl, ema_trades, ema_wr = get_metrics(portfolio_ema)
    cmb_pnl, cmb_trades, cmb_wr = get_metrics(portfolio_combined)
    
    print(f"{'Total Return':<15} | {def_pnl:<16} | {ema_pnl:<15} | {cmb_pnl:<15}")
    print(f"{'Total Trades':<15} | {def_trades:<16} | {ema_trades:<15} | {cmb_trades:<15}")
    print(f"{'Win Rate':<15} | {def_wr:<16} | {ema_wr:<15} | {cmb_wr:<15}")
    print(f"{'Exec Time':<15} | {time_default:.1f}s{'':<12} | {time_ema:.1f}s{'':<11} | {time_combined:.1f}s")
    print("#"*70 + "\n")


if __name__ == "__main__":
    main()
