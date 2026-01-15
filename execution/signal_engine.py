def generate_signal(
    trend,
    choch,
    fib,
    double_bottom,
    double_top,
    min_confidence=0.6
):
    """
    Returns BUY / SELL / NO_TRADE
    """

    # ---- BUY LOGIC ----
    if double_bottom.get("detected"):
        if (trend == "UPTREND" or choch) and double_bottom["confidence"] >= min_confidence:
            confidence = double_bottom["confidence"]

            if fib["fib_confluence"]:
                confidence = min(confidence + fib["confidence"] * 0.2, 1.0)

            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "reason": "Double Bottom + Trend/Fib"
            }

    # ---- SELL LOGIC ----
    if double_top.get("detected"):
        if trend == "DOWNTREND" and double_top["confidence"] >= min_confidence:
            return {
                "signal": "SELL",
                "confidence": double_top["confidence"],
                "reason": "Double Top + Downtrend"
            }

    return {
        "signal": "NO_TRADE",
        "confidence": 0.0,
        "reason": "Conditions not met"
    }
