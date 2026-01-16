import pandas as pd


def rank_trades_daily(df, top_k=1):
    """
    Pick top K ML trades per day
    """
    selected = []

    for date, group in df.groupby("date"):
        group = group.sort_values("ml_probability", ascending=False)
        selected.append(group.head(top_k))

    return pd.concat(selected, ignore_index=True)
