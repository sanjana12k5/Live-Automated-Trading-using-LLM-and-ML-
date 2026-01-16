def simulate_trades(df, trades, sl_pct=0.02, tp_pct=0.04):
    """
    Simple trade simulator with fixed SL / TP
    """
    results = []

    for trade in trades:
        entry_date = trade["date"]
        entry_price = trade["price"]
        direction = trade["signal"]

        entry_idx = df.index[df["date"] == entry_date]
        if len(entry_idx) == 0:
            continue

        entry_idx = entry_idx[0]

        sl = entry_price * (1 - sl_pct) if direction == "BUY" else entry_price * (1 + sl_pct)
        tp = entry_price * (1 + tp_pct) if direction == "BUY" else entry_price * (1 - tp_pct)

        outcome = "OPEN"
        exit_price = entry_price

        for i in range(entry_idx + 1, len(df)):
            high = df["high"].iloc[i]
            low = df["low"].iloc[i]

            if direction == "BUY":
                if low <= sl:
                    exit_price = sl
                    outcome = "SL"
                    break
                if high >= tp:
                    exit_price = tp
                    outcome = "TP"
                    break
            else:
                if high >= sl:
                    exit_price = sl
                    outcome = "SL"
                    break
                if low <= tp:
                    exit_price = tp
                    outcome = "TP"
                    break

        confidence = trade.get("ml_probability", 1.0)
        pnl = confidence * (
            (exit_price - entry_price)
            if direction == "BUY"
            else (entry_price - exit_price)
        )

        results.append({
            "entry_date": entry_date,
            "exit_price": exit_price,
            "outcome": outcome,
            "pnl": pnl
        })

    return results
