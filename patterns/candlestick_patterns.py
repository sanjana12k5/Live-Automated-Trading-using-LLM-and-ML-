def detect_hammer(c):
    body = abs(c["close"] - c["open"])
    lower_wick = min(c["open"], c["close"]) - c["low"]
    upper_wick = c["high"] - max(c["open"], c["close"])

    return lower_wick > body * 1.2 and upper_wick < body * 0.5


def detect_engulfing(prev, curr):
    bullish = (
        prev["close"] < prev["open"] and
        curr["close"] > curr["open"] and
        curr["close"] > prev["open"]
    )

    bearish = (
        prev["close"] > prev["open"] and
        curr["close"] < curr["open"] and
        curr["close"] < prev["open"]
    )

    return bullish, bearish


def detect_three_white_soldiers(candles):
    return all(c["close"] > c["open"] for c in candles)


def detect_three_black_crows(candles):
    return all(c["close"] < c["open"] for c in candles)
