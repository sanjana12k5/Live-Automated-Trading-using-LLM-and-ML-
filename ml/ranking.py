def rank_trades(df, method="percentile", value=99.5):
    """
    Rank trades and return top candidates

    method:
      - "percentile": take top X percentile
      - "top_k": take top K rows
    """

    df = df.sort_values("ml_probability", ascending=False)

    if method == "percentile":
        cutoff = df["ml_probability"].quantile(value / 100)
        selected = df[df["ml_probability"] >= cutoff]

    elif method == "top_k":
        selected = df.head(int(value))

    else:
        raise ValueError("Invalid ranking method")

    return selected
