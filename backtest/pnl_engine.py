def simulate_trades(df, trades, base_sl=0.02, base_tp=0.04):
    """
    Trade simulator with ML-adaptive TP / SL
    """
    results = []

    for trade in trades:
        entry_date = trade["date"]
        entry_price = trade["price"]
        direction = trade["signal"]

        confidence = trade.get("ml_probability", 1.0)

        # 🔥 adaptive exits
        sl_pct = base_sl * (1 - confidence)
        tp_pct = base_tp * (1 + confidence)

        entry_idx = df.index[df["date"] == entry_date]
        if len(entry_idx) == 0:
            continue

        entry_idx = entry_idx[0]

        if direction == "BUY":
            sl = entry_price * (1 - sl_pct)
            tp = entry_price * (1 + tp_pct)
        else:
            sl = entry_price * (1 + sl_pct)
            tp = entry_price * (1 - tp_pct)

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

        pnl = (
            exit_price - entry_price
            if direction == "BUY"
            else entry_price - exit_price
        )

        results.append({
            "entry_date": entry_date,
            "confidence": confidence,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "outcome": outcome,
            "pnl": pnl
        })

    return results
