import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from data.processed.loader import load_stock
from features.feature_builder import build_features
from backtest.dataset_scan import scan_dataset


def get_all_symbols(path="data/raw/sandp500/all_stocks_5yr.csv"):
    df = pd.read_csv(path)
    return df["Name"].unique().tolist()


def process_symbol(symbol):
    try:
        df = load_stock(symbol)
        if len(df) < 300:
            return None

        features = build_features(df)
        signals = scan_dataset(df)

        if signals:
            signal_dates = {s["date"] for s in signals}
            features["label"] = features["date"].isin(signal_dates).astype(int)
        else:
            features["label"] = 0

        return features

    except Exception:
        return None


def build_global_dataset_parallel():
    symbols = get_all_symbols()
    print(f"Total symbols: {len(symbols)}")

    all_features = []

    with ProcessPoolExecutor() as executor:
        for result in tqdm(
            executor.map(process_symbol, symbols),
            total=len(symbols),
            desc="Processing symbols"
        ):
            if result is not None:
                all_features.append(result)

    return pd.concat(all_features, ignore_index=True)


def train_xgb_all_fast():
    dataset = build_global_dataset_parallel()

    print("\nDataset shape:", dataset.shape)
    print("Positive labels:", dataset["label"].sum())

    X = dataset.drop(columns=["date", "label"])
    y = dataset["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=False
    )

    pos_weight = (len(y_train) - y_train.sum()) / max(1, y_train.sum())

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1          # 🔥 USE ALL CORES
    )

    print("\nTraining XGBoost...")
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]

    print("\nProbability stats:")
    print("Min:", np.min(probs))
    print("Mean:", np.mean(probs))
    print("Max:", np.max(probs))

    print("\nTop 10 probabilities:")
    print(sorted(probs, reverse=True)[:10])


if __name__ == "__main__":
    train_xgb_all_fast()
