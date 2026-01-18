def body(c):
    return abs(c["close"] - c["open"])

def upper_wick(c):
    return c["high"] - max(c["open"], c["close"])

def lower_wick(c):
    return min(c["open"], c["close"]) - c["low"]

def is_bullish(c):
    return c["close"] > c["open"]

def is_bearish(c):
    return c["close"] < c["open"]


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
def detect_inverted_hammer(c):
    return (
        body(c) > 0 and
        upper_wick(c) > 2 * body(c) and
        lower_wick(c) < body(c)
    )
def detect_morning_star(candles):
    if len(candles) < 3:
        return False

    c1, c2, c3 = candles[-3:]

    return (
        is_bearish(c1) and
        body(c2) < body(c1) * 0.4 and
        is_bullish(c3) and
        c3["close"] > (c1["open"] + c1["close"]) / 2
    )
def detect_bullish_harami(prev, curr):
    return (
        is_bearish(prev) and
        is_bullish(curr) and
        curr["open"] > prev["close"] and
        curr["close"] < prev["open"]
    )
def detect_bullish_breakout(df, lookback=20):
    if len(df) < lookback:
        return False

    recent = df.iloc[-lookback:]
    last = df.iloc[-1]

    return (
        last["close"] > recent["high"].max() and
        last["volume"] > recent["volume"].mean() * 1.5
    )
def detect_shooting_star(c):
    return (
        body(c) > 0 and
        upper_wick(c) > 2 * body(c) and
        lower_wick(c) < body(c)
    )
def detect_evening_star(candles):
    if len(candles) < 3:
        return False

    c1, c2, c3 = candles[-3:]

    return (
        is_bullish(c1) and
        body(c2) < body(c1) * 0.4 and
        is_bearish(c3) and
        c3["close"] < (c1["open"] + c1["close"]) / 2
    )
def detect_bearish_harami(prev, curr):
    return (
        is_bullish(prev) and
        is_bearish(curr) and
        curr["open"] < prev["close"] and
        curr["close"] > prev["open"]
    )
def detect_bearish_breakdown(df, lookback=20):
    if len(df) < lookback:
        return False

    recent = df.iloc[-lookback:]
    last = df.iloc[-1]

    return (
        last["close"] < recent["low"].min() and
        last["volume"] > recent["volume"].mean() * 1.5
    )
