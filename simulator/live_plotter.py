import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import timezone


class LivePlotter:
    def __init__(self, symbol="SIMULATED"):
        self.symbol = symbol
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(15, 7))


    def _draw_candles(self, df):
        for _, row in df.iterrows():
            color = "green" if row["close"] >= row["open"] else "red"

            # wick
            self.ax.plot(
                [row["date"], row["date"]],
                [row["low"], row["high"]],
                color=color,
                linewidth=1
            )

            # body
            rect = Rectangle(
                (mdates.date2num(row["date"]) - 0.0006, min(row["open"], row["close"])),
                0.0012,
                abs(row["close"] - row["open"]),
                color=color,
                alpha=0.8
            )
            self.ax.add_patch(rect)

    def _draw_trades(self, trades):
        for t in trades:
            # entry
            self.ax.scatter(
                t["entry_date"],
                t["entry_price"],
                color="blue" if t["signal"] == "BUY" else "orange",
                marker="^" if t["signal"] == "BUY" else "v",
                s=120
            )

            # exit
            if "exit_date" in t:
                self.ax.scatter(
                    t["exit_date"],
                    t["exit_price"],
                    color="red",
                    marker="x",
                    s=120
                )

    def _draw_stats(self, trades, capital):
        wins = [t for t in trades if t.get("pnl", 0) > 0]
        losses = [t for t in trades if t.get("pnl", 0) <= 0]

        stats = (
            f"Capital: {capital:,.2f}\n"
            f"Trades: {len(trades)}\n"
            f"Wins: {len(wins)} | Losses: {len(losses)}\n"
            f"Win Rate: {(len(wins)/max(1,len(trades))*100):.1f}%"
        )

        self.ax.text(
            0.01, 0.98, stats,
            transform=self.ax.transAxes,
            verticalalignment="top",
            bbox=dict(facecolor="black", alpha=0.6),
            color="white",
            fontsize=11
        )

    def _draw_clock(self, current_time):
        clock = current_time.strftime("%Y-%m-%d  %H:%M:%S")
        self.ax.text(
            0.99, 0.98, f"Market Time\n{clock}",
            transform=self.ax.transAxes,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(facecolor="black", alpha=0.6),
            color="cyan",
            fontsize=11
        )

    def update(self, df, trades, capital):
        self.ax.clear()

        self._draw_candles(df.tail(200))
        self._draw_trades(trades)
        self._draw_stats(trades, capital)
        self._draw_clock(df["date"].iloc[-1])

        self.ax.set_title(f"{self.symbol} — LIVE DAY TRADING SIMULATION")

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")

        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax.grid(alpha=0.3)

        plt.pause(0.01)
