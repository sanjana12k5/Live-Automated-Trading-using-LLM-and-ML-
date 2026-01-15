from data.processed.loader import load_stock
from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch

df = load_stock("AAPL")

swings = detect_swings(df)
structure = label_structure(swings)

trend = detect_trend(structure)
choch = detect_choch(structure)

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
