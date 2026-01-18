import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch
from patterns.fib.confluence import fib_confluence
from patterns.chart_patterns import detect_double_bottom, detect_double_top
from patterns.candlestick_patterns import (
    detect_hammer,
    detect_inverted_hammer,
    detect_engulfing,
    detect_morning_star,
    detect_evening_star,
    detect_bullish_harami,
    detect_bearish_harami,
    detect_three_white_soldiers,
    detect_three_black_crows,
    detect_bullish_breakout,
    detect_bearish_breakdown,
)
def build_features(df, min_bars=100):
    rows = []

    df = df.copy()

    # ATR + RSI (safe assignment)
    atr = AverageTrueRange(
        high=df["high"], low=df["low"], close=df["close"], window=14
    ).average_true_range()

    rsi = RSIIndicator(df["close"], window=14).rsi()

    df.loc[:, "atr"] = atr
    df.loc[:, "rsi"] = rsi

    for i in range(min_bars, len(df)):
        slice_df = df.iloc[max(0, i - 300): i + 1]

        # -------- STRUCTURE --------
        swings = detect_swings(slice_df)
        if len(swings) < 5:
            continue

        structure = label_structure(swings)
        trend = detect_trend(structure)
        choch = detect_choch(structure)

        fib = fib_confluence(swings, slice_df)

        # -------- PRICE DATA --------
        prev = slice_df.iloc[-2]
        curr = slice_df.iloc[-1]
        last3 = slice_df.iloc[-3:].to_dict("records")

        # -------- CANDLESTICK PATTERNS --------
        bull_engulf, bear_engulf = detect_engulfing(prev, curr)

        features = {
            "date": curr["date"],
            "close": curr["close"],

            # Trend / Structure
            "trend": 1 if trend == "UPTREND" else -1 if trend == "DOWNTREND" else 0,
            "choch": int(choch),

            # Fibonacci
            "fib_confluence": int(fib["fib_confluence"]),
            "fib_strength": fib["confidence"],

            # Bullish patterns
            "hammer": int(detect_hammer(curr)),
            "inv_hammer": int(detect_inverted_hammer(curr)),
            "bull_engulf": int(bull_engulf),
            "morning_star": int(detect_morning_star(last3)),
            "bull_harami": int(detect_bullish_harami(prev, curr)),
            "three_white": int(detect_three_white_soldiers(last3)),
            "bull_breakout": int(detect_bullish_breakout(slice_df)),

            # Bearish patterns
            "bear_engulf": int(bear_engulf),
            "evening_star": int(detect_evening_star(last3)),
            "bear_harami": int(detect_bearish_harami(prev, curr)),
            "three_black": int(detect_three_black_crows(last3)),
            "bear_breakdown": int(detect_bearish_breakdown(slice_df)),

            # Indicators
            "atr": slice_df["atr"].iloc[-1],
            "rsi": slice_df["rsi"].iloc[-1],
            "volume_ratio": (
                curr["volume"] /
                slice_df["volume"].rolling(20).mean().iloc[-1]
                if slice_df["volume"].rolling(20).mean().iloc[-1] else 1
            ),
        }

        rows.append(features)

    return pd.DataFrame(rows)
