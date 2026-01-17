import pandas as pd
from ml.model import load_model


FEATURE_COLUMNS = [
    "close",
    "trend",
    "choch",
    "fib_confluence",
    "fib_strength",
    "double_bottom",
    "double_top",
    "pattern_conf",
    "atr",
    "rsi",
    "volume_ratio",
]


def predict_probabilities(model, features_df):
    """
    Safe inference with strict feature alignment
    """

    # Drop non-features
    X = features_df.copy()

    if "date" in X.columns:
        X = X.drop(columns=["date"])

    if "label" in X.columns:
        X = X.drop(columns=["label"])

    # Ensure all expected features exist
    for col in FEATURE_COLUMNS:
        if col not in X.columns:
            X[col] = 0.0

    # Enforce correct order
    X = X[FEATURE_COLUMNS]

    # Drop rows with NaNs
    X = X.dropna()

    if len(X) == 0:
        return features_df.iloc[0:0]

    probs = model.predict_proba(X)[:, 1]

    result = features_df.loc[X.index].copy()
    result["ml_probability"] = probs

    return result


