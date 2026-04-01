from simulator.live_simulator import run_live_simulation
from collections import defaultdict

p = run_live_simulation(symbol="AAPL", enable_plot=False)

print("=" * 50)
print("         VERIFICATION REPORT")
print("=" * 50)
print(f"Final Capital : ${p.cash:.2f}")
print(f"Total Trades  : {len(p.trade_log)}")

if p.trade_log:
    wins   = [t for t in p.trade_log if t["pnl"] > 0]
    losses = [t for t in p.trade_log if t["pnl"] <= 0]
    total_pnl = sum(t["pnl"] for t in p.trade_log)
    print(f"Wins          : {len(wins)}")
    print(f"Losses        : {len(losses)}")
    print(f"Win Rate      : {len(wins)/len(p.trade_log)*100:.1f}%")
    print(f"Total PnL     : ${total_pnl:.2f}")
    print()
    print("--- Pattern Breakdown (sorted by PnL) ---")
    stats = defaultdict(lambda: {"count": 0, "pnl": 0.0})
    for t in p.trade_log:
        pat = t.get("pattern", "Unknown")
        stats[pat]["count"] += 1
        stats[pat]["pnl"]   += t["pnl"]
    for pat, s in sorted(stats.items(), key=lambda x: -x[1]["pnl"]):
        print(f"  {pat:<28} trades={s['count']:<3}  pnl=${s['pnl']:.2f}")
else:
    print("No trades executed.")

print("=" * 50)

# Verify Long-Only: all trades should be BUY opens
signals_in_order = [t.get("signal", t.get("side", "?")) for t in p.trade_log]
print("\n[SANITY CHECK] Ensuring all entries are BUY...")
for t in p.trade_log:
    sig = t.get("signal", "?")
    if sig not in ["BUY"]:
        print(f"  WARNING: unexpected signal '{sig}' in trade log!")
        break
else:
    print("  All trade entries are BUY only. Long-Only constraint is working correctly.")
