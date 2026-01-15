from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch
from patterns.fib.confluence import fib_confluence
from patterns.chart_patterns import detect_double_bottom, detect_double_top
from execution.signal_engine import generate_signal


def scan_dataset(df, min_bars=100):
    """
    Runs signal engine on entire dataset candle-by-candle
    """
    results = []

    for i in range(min_bars, len(df)):
        slice_df = df.iloc[:i].copy()

        swings = detect_swings(slice_df)
        if len(swings) < 5:
            continue

        structure = label_structure(swings)
        trend = detect_trend(structure)
        choch = detect_choch(structure)

        fib = fib_confluence(swings, slice_df)

        db = detect_double_bottom(structure)
        dt = detect_double_top(structure)

        signal = generate_signal(
            trend=trend,
            choch=choch,
            fib=fib,
            double_bottom=db,
            double_top=dt
        )

        if signal["signal"] != "NO_TRADE":
            results.append({
                "index": i,
                "date": slice_df["date"].iloc[-1],
                "price": slice_df["close"].iloc[-1],
                "signal": signal["signal"],
                "confidence": signal["confidence"],
                "trend": trend
            })

    return results
