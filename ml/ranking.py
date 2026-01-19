import pandas as pd


def rank_trades_daily(df, top_k=2):
    df = df.copy()

    # Core scoring formula
    df["score"] = (
        df["ml_probability"] * 0.5 +
        df["fib_strength"] * 0.2 +
        (df["volume_ratio"].clip(0, 3) / 3) * 0.15 +
        (1 - abs(df["rsi"] - 50) / 50) * 0.15
    )

    # Penalize chop
    df.loc[df["atr"] < df["atr"].rolling(20).mean(), "score"] *= 0.6

    return df.sort_values("score", ascending=False).head(top_k)
