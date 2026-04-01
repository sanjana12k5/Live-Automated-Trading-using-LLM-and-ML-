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
    return df["Name"].unique().tolist()[:50]


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
    return dataset


def train_xgb_daytrading():
    dataset = build_global_dataset()

    print("\nDataset shape:", dataset.shape)
    print("Positive trades:", dataset["label"].sum())

    X = dataset.drop(columns=["date", "label"])
    y = dataset["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, shuffle=False
    )

    # Handle class imbalance
    pos_weight = (len(y_train) - y_train.sum()) / max(1, y_train.sum())

    model = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.04,
        subsample=0.75,
        colsample_bytree=0.75,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining XGBoost...")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))

    print("\nClassification Report:")
    print(classification_report(y_test, preds, digits=4))

    print("\nProbability stats:")
    print("Min:", probs.min())
    print("Mean:", probs.mean())
    print("Max:", probs.max())

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")


if __name__ == "__main__":
    train_xgb_daytrading()
