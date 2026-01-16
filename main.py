from data.processed.loader import load_stock
from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch

df = load_stock("AAPL")

swings = detect_swings(df)
structure = label_structure(swings)

trend = detect_trend(structure)
choch = detect_choch(structure)

"""
print("Trend:", trend)
print("CHOCH:", choch)

print("Last 5 structure points:")
for s in structure[-5:]:
    print(s)
from patterns.fib.confluence import fib_confluence

fib = fib_confluence(swings, df)

print("Fib Confluence:")
print(fib)
from patterns.chart_patterns import detect_double_bottom, detect_double_top

db = detect_double_bottom(structure)
dt = detect_double_top(structure)

print("Double Bottom:", db)
print("Double Top:", dt)
from execution.signal_engine import generate_signal

signal = generate_signal(
    trend=trend,
    choch=choch,
    fib=fib,
    double_bottom=db,
    double_top=dt
)

print("FINAL SIGNAL:")
print(signal)
from data.processed.loader import load_stock
from backtest.dataset_scan import scan_dataset

df = load_stock("AAPL")

signals = scan_dataset(df)

print(f"Total signals found: {len(signals)}")

for s in signals[:10]:
    print(s)
buys = [s for s in signals if s["signal"] == "BUY"]
sells = [s for s in signals if s["signal"] == "SELL"]

print("BUY signals:", len(buys))
print("SELL signals:", len(sells))


from data.processed.loader import load_stock
from features.feature_builder import build_features

df = load_stock("AAPL")

features = build_features(df)

print(features.head())
print(features.describe())

from ml.pipeline import run_ml_pipeline

top_trades = run_ml_pipeline("AAPL")

print(top_trades[["date", "close", "ml_probability"]].head(10))

from backtest.ml_vs_rule import compare_ml_vs_rule

rule_trades, ml_trades = compare_ml_vs_rule("AAPL")

print("RULE TRADES:", len(rule_trades))
print("ML TRADES:", len(ml_trades))

print("\nTop ML trades:")
print(ml_trades[["date", "close", "ml_probability"]].head(10))
"""
from backtest.ml_vs_rule import compare_ml_vs_rule
from backtest.pnl_engine import simulate_trades
from backtest.equity_curve import plot_equity_curve
from data.processed.loader import load_stock

df = load_stock("AAPL")

rule_trades, ml_trades = compare_ml_vs_rule("AAPL")

rule_results = simulate_trades(df, rule_trades)
ml_results = simulate_trades(df, ml_trades)


print("Rule PnL:", sum(r["pnl"] for r in rule_results))
print("ML PnL:", sum(r["pnl"] for r in ml_results))

plot_equity_curve(rule_results, "Rule-Based Equity")
plot_equity_curve(ml_results, "ML-Ranked Equity")
print("Avg position size:",
      sum(r["position_size"] for r in ml_results) / len(ml_results))

print("Max position size:",
      max(r["position_size"] for r in ml_results))
