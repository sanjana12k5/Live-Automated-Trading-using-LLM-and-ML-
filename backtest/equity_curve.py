import matplotlib.pyplot as plt


def plot_equity_curve(results, title="Equity Curve"):
    equity = [0]
    for r in results:
        equity.append(equity[-1] + r["pnl"])

    plt.figure()
    plt.plot(equity)
    plt.title(title)
    plt.xlabel("Trades")
    plt.ylabel("PnL")
    plt.show()
