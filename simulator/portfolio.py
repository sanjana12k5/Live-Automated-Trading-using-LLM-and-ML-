class Portfolio:
    def __init__(self, initial_capital=100000):
        self.cash = initial_capital
        self.positions = []
        self.trade_log = []

    def has_open_position(self):
        return len(self.positions) > 0

    def open_position(self, trade):
        self.positions.append(trade)

    def close_position(self, trade, exit_price, date, reason):
        # ---- PnL calculation ----
        pnl = (
            exit_price - trade["entry_price"]
            if trade["signal"] == "BUY"
            else trade["entry_price"] - exit_price
        )

        self.cash += pnl

        # ---- Trade log (for plotter + stats) ----
        self.trade_log.append({
            "entry_date": trade["entry_date"],
            "exit_date": date,
            "entry_price": trade["entry_price"],
            "exit_price": exit_price,
            "signal": trade["signal"],
            "confidence": trade["confidence"],
            "pattern": trade.get("pattern"),
            "pnl": pnl,
            "reason": reason,
        })

        self.positions.remove(trade)
