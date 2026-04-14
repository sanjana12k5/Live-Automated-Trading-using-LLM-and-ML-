import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

from data.processed.loader import load_stock
from features.feature_builder import build_features
from backtest.dataset_scan import scan_dataset


MODEL_PATH = "ml/models/xgb_global_model.pkl"


def get_all_symbols(path="data/raw/sandp500/all_stocks_5yr.csv"):
    df = pd.read_csv(path)
    return df["Name"].unique().tolist()


def process_symbol(symbol):
    try:
        df = load_stock(symbol)
        if len(df) < 300:
            return None

        features = build_features(df)
        if features.empty:
            return None

        signals = scan_dataset(df)
        profitable_dates = set()

        for s in signals:
            if s["signal"] != "BUY":
                continue

            entry_date = s["date"]
            entry_price = s["price"]

            feat_row = features[features["date"] == entry_date]
            if feat_row.empty:
                continue
            atr = feat_row.iloc[0]["atr"]

            if pd.isna(atr) or atr <= 0:
                continue

            sl = entry_price - (atr * 1.0)
            tp = entry_price + (atr * 2.0)

            idx_series = df.index[df["date"] == entry_date]
            if len(idx_series) == 0:
                continue
            entry_idx = idx_series[0]

            is_profitable = False
            for i in range(entry_idx + 1, len(df)):
                low = df["low"].iloc[i]
                high = df["high"].iloc[i]

                if low <= sl:
                    is_profitable = False
                    break
                if high >= tp:
                    is_profitable = True
                    break

            if is_profitable:
                profitable_dates.add(entry_date)

        features["label"] = features["date"].isin(profitable_dates).astype(int)
        return features

    except Exception as e:
        print(f"Error in {symbol}: {e}")
        return None

def build_global_dataset():
    import os
    import pickle
    cache_path = "data/processed/full_dataset.pkl"
    if os.path.exists(cache_path):
        print("Loading dataset from cache...")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    symbols = get_all_symbols()
    print(f"Total symbols: {len(symbols)}")

    all_rows = []

    with ProcessPoolExecutor() as executor:
        for result in tqdm(
            executor.map(process_symbol, symbols),
            total=len(symbols),
            desc="Building dataset"
        ):
            if result is not None:
                all_rows.append(result)

    dataset = pd.concat(all_rows, ignore_index=True)
    with open(cache_path, "wb") as f:
        pickle.dump(dataset, f)
    return dataset



def train_xgb_daytrading():
    dataset = build_global_dataset()

    print("\nDataset shape:", dataset.shape)
    print("Positive trades:", dataset["label"].sum())

    X = dataset.drop(columns=["label"])
    y = dataset["label"]

    X_train_full, X_test_full, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=False
    )

    X_train = X_train_full.drop(columns=["date"])
    X_test = X_test_full.drop(columns=["date"])

    # Handle class imbalance
    pos_weight = (len(y_train) - y_train.sum()) / max(1, y_train.sum())

    model = XGBClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.03,
        gamma=2.0,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining XGBoost...")
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]

    # Dynamically find a threshold where False Positives <= 0.1 * len(y_test)
    threshold = 0.50
    for t in np.arange(0.50, 1.00, 0.01):
        test_preds = (probs > t).astype(int)
        fps_count = ((y_test == 0) & (test_preds == 1)).sum()
        if fps_count <= 0.1 * len(y_test):
            threshold = t
            break

    print(f"\nOptimal Dynamic Threshold for <10% FPs: {threshold:.2f}")
    preds = (probs > threshold).astype(int)

    print("\nConfusion Matrix (Dynamic Threshold):")
    print(confusion_matrix(y_test, preds))

    print("\nClassification Report (Dynamic Threshold):")
    print(classification_report(y_test, preds, digits=4))

    print("\n================ User Specific Thresholds ================")
    for thresh in [0.80, 0.85, 0.90]:
        t_preds = (probs > thresh).astype(int)
        cm = confusion_matrix(y_test, t_preds)
        print(f"\n=== Threshold: {thresh} ===")
        print(cm)
        print(classification_report(y_test, t_preds, digits=4))
        fps_t = ((y_test == 0) & (t_preds == 1)).sum()
        fns_t = ((y_test == 1) & (t_preds == 0)).sum()
        print(f"False Positives: {fps_t}")
        print(f"False Negatives: {fns_t}")
    print("==========================================================\n")

    print("\nProbability stats:")
    print("Min:", probs.min())
    print("Mean:", probs.mean())
    print("Max:", probs.max())

    # --- Failure Analysis ---
    failure_df = X_test_full.copy()
    failure_df["actual"] = y_test
    failure_df["predicted"] = preds
    failure_df["probability"] = probs
    
    # False positives and False negatives
    failures = failure_df[failure_df["actual"] != failure_df["predicted"]]
    fps = failures[(failures["actual"] == 0) & (failures["predicted"] == 1)]
    fns = failures[(failures["actual"] == 1) & (failures["predicted"] == 0)]
    
    print(f"\nFailure Analysis:")
    print(f"Total failures: {len(failures)} / {len(y_test)}")
    print(f"False Positives: {len(fps)}")
    print(f"False Negatives: {len(fns)}")
    
    # Sort by probability to see worst False Positives
    fps_sorted = fps.sort_values(by="probability", ascending=False)
    
    # Save failures
    failures_out_path = "ml/models/failures_analysis.csv"
    fps_sorted.to_csv(failures_out_path, index=False)
    print(f"\nFailures saved to -> {failures_out_path}")

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved -> {MODEL_PATH}")


if __name__ == "__main__":
    train_xgb_daytrading()
