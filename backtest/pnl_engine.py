def simulate_trades(
    df,
    trades,
    base_sl=0.02,
    base_tp=0.04,
    base_risk=1.0
):
    """
    Trade simulator with:
    - ML-adaptive TP/SL
    - Volatility-normalized position sizing
    """

    results = []

    for trade in trades:
        entry_date = trade["date"]
        entry_price = trade["price"]
        direction = trade["signal"]

        confidence = trade.get("ml_probability", 1.0)
        atr = trade.get("atr", None)

        # skip if ATR missing
        if atr is None or atr <= 0:
            continue

        # -------------------------------
        # Adaptive TP / SL
        # -------------------------------
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

        # -------------------------------
        # Position sizing (VOLATILITY)
        # -------------------------------
        position_size = base_risk * (confidence / atr)

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

        raw_pnl = (
            exit_price - entry_price
            if direction == "BUY"
            else entry_price - exit_price
        )

        pnl = position_size * raw_pnl

        results.append({
            "entry_date": entry_date,
            "confidence": confidence,
            "atr": atr,
            "position_size": position_size,
            "outcome": outcome,
            "pnl": pnl
        })

    return results
