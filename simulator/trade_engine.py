def check_exit(trade, candle):
    high = candle["high"]
    low = candle["low"]

    if trade["signal"] == "BUY":
        if low <= trade["sl"]:
            return trade["sl"], "SL"
        if high >= trade["tp"]:
            return trade["tp"], "TP"
    else:
        if high >= trade["sl"]:
            return trade["sl"], "SL"
        if low <= trade["tp"]:
            return trade["tp"], "TP"

    return None, None
