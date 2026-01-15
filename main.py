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
"""

from data.processed.loader import load_stock
from features.feature_builder import build_features

df = load_stock("AAPL")

features = build_features(df)

print(features.head())
print(features.describe())
