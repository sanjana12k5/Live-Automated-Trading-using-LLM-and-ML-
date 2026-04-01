import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def detect_swings(df, window=3):
    swings = []

    if len(df) < window * 2 + 1:
        return swings

    highs = df["high"].values
    lows = df["low"].values

    swing_high_idx = argrelextrema(highs, np.greater, order=window)[0]
    swing_low_idx = argrelextrema(lows, np.less, order=window)[0]

    for idx in swing_high_idx:
        if window <= idx < len(df) - window:
            swings.append((df.index[idx], "HIGH", highs[idx], idx))

    for idx in swing_low_idx:
        if window <= idx < len(df) - window:
            swings.append((df.index[idx], "LOW", lows[idx], idx))

    swings.sort(key=lambda x: x[3])

    return [(s[0], s[1], s[2]) for s in swings]
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
