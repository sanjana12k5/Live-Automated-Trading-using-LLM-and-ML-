from patterns.fib.retracement import calculate_fib

def fib_confluence(swings, df, lookback_swings=6, tolerance=0.003):
    """
    Detects Fibonacci confluence using multiple recent swings
    """
    fib_prices = []

    recent = swings[-lookback_swings:]

    for i in range(len(recent) - 1):
        s1 = recent[i]
        s2 = recent[i + 1]

        if s1[1] == "HIGH" and s2[1] == "LOW":
            high, low = s1[2], s2[2]
        elif s1[1] == "LOW" and s2[1] == "HIGH":
            high, low = s2[2], s1[2]
        else:
            continue

        fibs = calculate_fib(high, low)
        fib_prices.extend(fibs.values())

    current_price = df["close"].iloc[-1]

    matches = [
        price for price in fib_prices
        if abs(price - current_price) / current_price <= tolerance
    ]

    return {
        "fib_confluence": len(matches) >= 2,
        "match_count": len(matches),
        "confidence": min(len(matches) / 3, 1.0),
        "levels": matches
    }
