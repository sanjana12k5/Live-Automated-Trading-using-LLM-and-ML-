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
        # --- PnL ---
        pnl = (
            exit_price - trade["entry_price"]
            if trade["signal"] == "BUY"
            else trade["entry_price"] - exit_price
        )

        self.cash += pnl

        # ✅ LOG EVERYTHING THE PLOTTER NEEDS
        self.trade_log.append({
            "entry_date": trade["entry_date"],
            "exit_date": date,
            "entry_price": trade["entry_price"],   # ✅ FIX
            "exit_price": exit_price,               # ✅ FIX
            "signal": trade["signal"],
            "confidence": trade["confidence"],
            "pattern": trade.get("pattern"),
            "pnl": pnl,
            "reason": reason,
        })

        self.positions.remove(trade)
