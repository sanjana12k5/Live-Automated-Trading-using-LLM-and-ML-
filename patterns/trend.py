def detect_trend(structure, lookback=5):
    recent = structure[-lookback:]

    highs = [s for s in recent if s[1] == "HIGH"]
    lows = [s for s in recent if s[1] == "LOW"]

    if len(highs) < 2 or len(lows) < 2:
        return "RANGE"

    if highs[-1][3] == "HH" and lows[-1][3] == "HL":
        return "UPTREND"

    if highs[-1][3] == "LH" and lows[-1][3] == "LL":
        return "DOWNTREND"

    return "RANGE"
def detect_choch(structure):
    if len(structure) < 4:
        return False

    last = structure[-1]
    prev = structure[-2]

    # Uptrend failure
    if prev[3] == "HL" and last[3] == "LL":
        return True

    # Downtrend failure
    if prev[3] == "LH" and last[3] == "HH":
        return True

    return False
