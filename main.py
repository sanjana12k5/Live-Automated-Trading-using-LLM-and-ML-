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
