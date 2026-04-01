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
    detect_shooting_star,
)
from execution.signal_engine import generate_signal


def scan_dataset(df, min_bars=100, cooldown_period=10):
    results = []

    position = None          # None | "LONG" | "SHORT"
    cooldown = 0             # candles remaining before new trade

    for i in range(min_bars, len(df)):
        slice_df = df.iloc[max(0, i - 300):i].copy()

        # ⏸️ COOLDOWN CHECK (FIRST THING)
        if cooldown > 0:
            cooldown -= 1
            continue

        swings = detect_swings(slice_df)
        if len(swings) < 5:
            continue

        structure = label_structure(swings)
        trend = detect_trend(structure)
        choch = detect_choch(structure)
        fib = fib_confluence(swings, slice_df)

        db = detect_double_bottom(structure)
        dt = detect_double_top(structure)

        # Candlestick Patterns
        prev = slice_df.iloc[-2]
        curr = slice_df.iloc[-1]
        last3 = slice_df.iloc[-3:].to_dict("records")

        hammer = detect_hammer(curr)
        inv_hammer = detect_inverted_hammer(curr)
        bull_engulf, bear_engulf = detect_engulfing(prev, curr)
        morning_star = detect_morning_star(last3)
        bull_harami = detect_bullish_harami(prev, curr)
        three_white = detect_three_white_soldiers(last3)
        bull_breakout = detect_bullish_breakout(slice_df)

        shooting_star = detect_shooting_star(curr)
        evening_star = detect_evening_star(last3)
        bear_harami = detect_bearish_harami(prev, curr)
        three_black = detect_three_black_crows(last3)
        bear_breakdown = detect_bearish_breakdown(slice_df)

        signal = generate_signal(
            trend=trend,
            choch=choch,
            hammer=hammer,
            inv_hammer=inv_hammer,
            bull_engulf=bull_engulf,
            morning_star=morning_star,
            bull_harami=bull_harami,
            three_white=three_white,
            bull_breakout=bull_breakout,
            bear_engulf=bear_engulf,
            shooting_star=shooting_star,
            evening_star=evening_star,
            bear_harami=bear_harami,
            three_black=three_black,
            bear_breakdown=bear_breakdown,
            fib=fib,
            double_bottom=db,
            double_top=dt
        )

        action = signal["signal"]

        if action == "BUY" and position is None:
            position = "LONG"
            cooldown = cooldown_period

            results.append({
                "index": i,
                "date": slice_df["date"].iloc[-1],
                "price": slice_df["close"].iloc[-1],
                "signal": "BUY",
                "confidence": signal["confidence"],
                "trend": trend
            })
            
        elif action == "SELL" and position == "LONG":
            position = None
            cooldown = cooldown_period

            results.append({
                "index": i,
                "date": slice_df["date"].iloc[-1],
                "price": slice_df["close"].iloc[-1],
                "signal": "SELL", 
                "confidence": signal["confidence"],
                "trend": trend
            })

    return results
