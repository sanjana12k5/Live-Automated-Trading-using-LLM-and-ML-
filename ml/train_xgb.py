import os
import numpy as np
import pandas as pd
from tqdm import tqdm

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

from data.processed.loader import load_stock
from features.feature_builder import build_features
from backtest.dataset_scan import scan_dataset
from ml.model import save_model


# -------------------------------------------------
# CONFIG (important for Windows stability)
# -------------------------------------------------
os.environ["OMP_NUM_THREADS"] = "1"


# -------------------------------------------------
# Load all symbols
# -------------------------------------------------
def get_all_symbols(path="data/raw/sandp500/all_stocks_5yr.csv"):
    df = pd.read_csv(path)
    return df["Name"].unique().tolist()


# -------------------------------------------------
# Build dataset SEQUENTIALLY (fast + safe)
# -------------------------------------------------
def build_global_dataset():
    symbols = get_all_symbols()
    print(f"Total symbols: {len(symbols)}")

    all_features = []
    processed = 0
    skipped = 0

    for symbol in tqdm(symbols, desc="Processing symbols"):
        try:
            df = load_stock(symbol)

            if df is None or len(df) < 300:
                skipped += 1
                continue

            # 🔥 compute signals ONCE per symbol
            signals = scan_dataset(df)
            signal_dates = {s["date"] for s in signals}

            # 🔥 build features ONCE per symbol
            features = build_features(df)

            # 🔥 label via O(1) lookup
            features["label"] = features["date"].isin(signal_dates).astype(int)

            all_features.append(features)
            processed += 1

        except Exception as e:
            skipped += 1
            print(f"[SKIP] {symbol}: {e}")

    print("\nSUMMARY")
    print("Processed symbols:", processed)
    print("Skipped symbols:", skipped)

    if len(all_features) == 0:
        raise RuntimeError("No data generated — check feature builder")

    return pd.concat(all_features, ignore_index=True)


# -------------------------------------------------
# Train XGBoost on full dataset
# -------------------------------------------------
def train_xgb_all():
    dataset = build_global_dataset()

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
        n_jobs=-1
    )

    print("\nTraining XGBoost...")
    model.fit(X_train, y_train)

    # 🔥 SAVE MODEL (THIS WAS MISSING EARLIER)
    save_model(model)

    # -------------------------------------------------
    # Inspect probabilities (ranking sanity check)
    # -------------------------------------------------
    probs = model.predict_proba(X_test)[:, 1]

    print("\nProbability stats:")
    print("Min :", np.min(probs))
    print("Mean:", np.mean(probs))
    print("Max :", np.max(probs))

    print("\nTop 10 probabilities:")
    print(sorted(probs, reverse=True)[:10])


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    train_xgb_all()
