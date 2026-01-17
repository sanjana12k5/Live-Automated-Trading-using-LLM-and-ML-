import matplotlib.pyplot as plt
import pandas as pd


def plot_simulation(df, trades, symbol="AAPL"):
    """
    Visual replay of price + ML trades
    """

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    fig, ax = plt.subplots(figsize=(15, 7))

    # ---- PRICE LINE ----
    ax.plot(df["date"], df["close"], color="black", linewidth=1.2, label="Close Price")

    # ---- TRADES ----
    for trade in trades:
        entry_date = trade["entry_date"]
        exit_date = trade["exit_date"]
        pnl = trade["pnl"]

        entry_price = df.loc[df["date"] == entry_date, "close"].values[0]
        exit_price = df.loc[df["date"] == exit_date, "close"].values[0]

        # BUY marker
        ax.scatter(entry_date, entry_price, color="green", marker="^", s=120)

        # SELL / EXIT marker
        ax.scatter(exit_date, exit_price, color="red", marker="v", s=120)

        # Trade line
        ax.plot(
            [entry_date, exit_date],
            [entry_price, exit_price],
            color="green" if pnl > 0 else "red",
            linewidth=2,
            alpha=0.8,
        )

    ax.set_title(f"{symbol} – ML Trading Simulation", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
