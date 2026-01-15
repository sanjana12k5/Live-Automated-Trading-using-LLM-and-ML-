import pandas as pd

def detect_swings(df, window=3):
    swings = []

    for i in range(window, len(df) - window):
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]

        is_swing_high = all(
            high > df["high"].iloc[i - j] and high > df["high"].iloc[i + j]
            for j in range(1, window + 1)
        )

        is_swing_low = all(
            low < df["low"].iloc[i - j] and low < df["low"].iloc[i + j]
            for j in range(1, window + 1)
        )

        if is_swing_high:
            swings.append((df.index[i], "HIGH", high))

        if is_swing_low:
            swings.append((df.index[i], "LOW", low))

    return swings
def label_structure(swings):
    structure = []
    last_high = None
    last_low = None

    for idx, swing_type, price in swings:
        if swing_type == "HIGH":
            if last_high is None:
                label = "HH"
            else:
                label = "HH" if price > last_high else "LH"
            last_high = price

        else:  # LOW
            if last_low is None:
                label = "HL"
            else:
                label = "HL" if price > last_low else "LL"
            last_low = price

        structure.append((idx, swing_type, price, label))

    return structure
