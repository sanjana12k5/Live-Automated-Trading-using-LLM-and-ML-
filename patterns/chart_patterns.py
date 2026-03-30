def detect_double_bottom(structure, tolerance=0.01):
    lows = [s for s in structure if s[1] == "LOW"]

    if len(lows) < 2:
        return {"detected": False}

    l1, l2 = lows[-2], lows[-1]

    # avoid division issues
    if l1[2] == 0:
        return {"detected": False}

    price_diff = abs(l1[2] - l2[2]) / l1[2]

    if price_diff <= tolerance and l2[3] == "HL":
        confidence = 1 - price_diff
        confidence = max(0.6, min(confidence, 0.85))  # HARD CAP

        return {
            "detected": True,
            "type": "double_bottom",
            "confidence": round(confidence, 2)
        }

    return {"detected": False}


def detect_double_top(structure, tolerance=0.01):
    highs = [s for s in structure if s[1] == "HIGH"]

    if len(highs) < 2:
        return {"detected": False}

    h1, h2 = highs[-2], highs[-1]

    # avoid division issues
    if h1[2] == 0:
        return {"detected": False}

    price_diff = abs(h1[2] - h2[2]) / h1[2]

    if price_diff <= tolerance and h2[3] == "LH":
        confidence = 1 - price_diff
        confidence = max(0.6, min(confidence, 0.85))  # HARD CAP

        return {
            "detected": True,
            "type": "double_top",
            "confidence": round(confidence, 2)
        }

    return {"detected": False}
