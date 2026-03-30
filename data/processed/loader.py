import pandas as pd

def load_stock(symbol, path="data/raw/sandp500/all_stocks_5yr.csv"):
    df = pd.read_csv(path)

    # normalize column names
    df.columns = [c.lower() for c in df.columns]

    df = df[df["name"] == symbol].copy()

    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[["date", "open", "high", "low", "close", "volume"]]
