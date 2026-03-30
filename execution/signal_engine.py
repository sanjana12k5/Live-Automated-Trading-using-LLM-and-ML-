def generate_signal(
    trend,
    choch,
    fib,
    hammer,
    inv_hammer,
    bull_engulf,
    morning_star,
    bull_harami,
    three_white,
    bull_breakout,
    bear_engulf,
    shooting_star,
    evening_star,
    bear_harami,
    three_black,
    bear_breakdown,
    double_bottom,
    double_top,
    min_confidence=0.6
):
    """
    Returns BUY / SELL / NO_TRADE
    """
    
    # ---- BUY LOGIC ----
    signal = None
    reason = None
    confidence = 0.0

    # 1. Double Bottom (High Quality)
    if double_bottom.get("detected"):
        if (trend == "UPTREND" or choch) and double_bottom["confidence"] >= min_confidence:
            signal = "BUY"
            confidence = double_bottom["confidence"]
            reason = "Double Bottom"

    # 2. Candlestick Patterns
    elif hammer:
        signal = "BUY"
        confidence = 0.65
        reason = "Hammer"
    elif inv_hammer:
        signal = "BUY"
        confidence = 0.60
        reason = "Inverted Hammer"
    elif bull_engulf:
        signal = "BUY"
        confidence = 0.70
        reason = "Bullish Engulfing"
    elif morning_star:
        signal = "BUY"
        confidence = 0.75
        reason = "Morning Star"
    elif bull_harami:
        signal = "BUY"
        confidence = 0.60
        reason = "Bullish Harami"
    elif three_white:
        signal = "BUY"
        confidence = 0.80
        reason = "3 White Soldiers"
    elif bull_breakout:
        signal = "BUY"
        confidence = 0.75
        reason = "Bullish Breakout"

    # ---- SELL LOGIC ----
    # 1. Double Top (High Quality)
    if not signal and double_top.get("detected"):
        if trend == "DOWNTREND" and double_top["confidence"] >= min_confidence:
            signal = "SELL"
            confidence = double_top["confidence"]
            reason = "Double Top"

    # 2. Candlestick Patterns
    elif not signal:
        if bear_engulf:
            signal = "SELL"
            confidence = 0.70
            reason = "Bearish Engulfing"
        elif shooting_star:
            signal = "SELL"
            confidence = 0.65
            reason = "Shooting Star"
        elif evening_star:
            signal = "SELL"
            confidence = 0.75
            reason = "Evening Star"
        elif bear_harami:
            signal = "SELL"
            confidence = 0.60
            reason = "Bearish Harami"
        elif three_black:
            signal = "SELL"
            confidence = 0.80
            reason = "3 Black Crows"
        elif bear_breakdown:
            signal = "SELL"
            confidence = 0.75
            reason = "Bearish Breakdown"

    # ---- FINAL CONFLUENCE CHECK ----
    if signal:
        # Boost confidence if trend aligns
        if signal == "BUY" and trend == "UPTREND":
            confidence += 0.1
        elif signal == "SELL" and trend == "DOWNTREND":
            confidence += 0.1

        # Boost if Fib confluence matches
        if fib["fib_confluence"]:
             confidence += fib["confidence"] * 0.1

        # 🔒 GLOBAL HARD CAP
        confidence = max(0.6, min(confidence, 0.95))
        
        return {
            "signal": signal,
            "confidence": round(confidence, 2),
            "reason": reason
        }

    return {
        "signal": "NO_TRADE",
        "confidence": 0.0,
        "reason": "Conditions not met"
    }
