import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch
from patterns.fib.confluence import fib_confluence
from patterns.chart_patterns import detect_double_bottom, detect_double_top


def build_features(df, min_bars=100):
    rows = []

    atr_indicator = AverageTrueRange(
        high=df["high"], low=df["low"], close=df["close"], window=14
    )
    df["atr"] = atr_indicator.average_true_range()

    rsi_indicator = RSIIndicator(df["close"], window=14)
    df["rsi"] = rsi_indicator.rsi()

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

        rows.append({
            "date": slice_df["date"].iloc[-1],
            "close": slice_df["close"].iloc[-1],
            "trend": 1 if trend == "UPTREND" else -1 if trend == "DOWNTREND" else 0,
            "choch": int(choch),
            "fib_confluence": int(fib["fib_confluence"]),
            "fib_strength": fib["confidence"],
            "double_bottom": int(db.get("detected", False)),
            "double_top": int(dt.get("detected", False)),
            "pattern_conf": max(db.get("confidence", 0), dt.get("confidence", 0)),
            "atr": slice_df["atr"].iloc[-1],
            "rsi": slice_df["rsi"].iloc[-1],
            "volume_ratio": slice_df["volume"].iloc[-1] /
                            slice_df["volume"].rolling(20).mean().iloc[-1]
                            if slice_df["volume"].rolling(20).mean().iloc[-1] else 1
        })

    return pd.DataFrame(rows)
