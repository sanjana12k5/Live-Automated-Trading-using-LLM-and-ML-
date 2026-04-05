from simulator.live_simulator import run_live_simulation

print("Starting simulation without plotting...")
portfolio = run_live_simulation(symbol="AAPL", enable_plot=False)

print("\n--- Generating Clean Report ---")
with open("simulation_analysis.txt", "w", encoding="utf-8") as f:
    f.write("="*40 + "\n")
    f.write("       SIMULATION PERFORMANCE REPORT       \n")
    f.write("="*40 + "\n")
    f.write(f"Final Capital: ${portfolio.cash:.2f}\n")
    f.write(f"Total Return : ${portfolio.cash - 100000:.2f} ({(portfolio.cash - 100000)/1000:.2f}%)\n")
    f.write(f"Total Trades : {len(portfolio.trade_log)}\n")

    if portfolio.trade_log:
        wins = [t for t in portfolio.trade_log if t["pnl"] > 0]
        losses = [t for t in portfolio.trade_log if t["pnl"] <= 0]
        
        win_rate = (len(wins) / len(portfolio.trade_log)) * 100
        avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0.0
        avg_loss = sum(t["pnl"] for t in losses) / len(losses) if losses else 0.0
        
        f.write(f"Win Rate     : {win_rate:.2f}%\n")
        f.write(f"Avg Win      : ${avg_win:.2f}\n")
        f.write(f"Avg Loss     : ${avg_loss:.2f}\n")
        f.write("-" * 40 + "\n")
        
        f.write("\nPerformance by Pattern:\n")
        from collections import defaultdict
        pattern_stats = defaultdict(lambda: {"count": 0, "pnl": 0.0})
        
        for t in portfolio.trade_log:
            pat = t.get("pattern", "Unknown")
            pattern_stats[pat]["count"] += 1
            pattern_stats[pat]["pnl"] += t["pnl"]
            
        for pat, stats in pattern_stats.items():
            f.write(f"{pat:<20} | Count: {stats['count']:<3} | PnL: ${stats['pnl']:.2f}\n")

    f.write("="*40 + "\n")

    f.write("\n--- ALL SUGGESTIONS (TRADE LOG) ---\n")
    for t in portfolio.trade_log:
        f.write(f"Date: {t['entry_date']} | {t['signal']} | Pattern: {t['pattern']} | PNL: ${t['pnl']:.2f}\n")

print("Report saved to simulation_analysis.txt")
