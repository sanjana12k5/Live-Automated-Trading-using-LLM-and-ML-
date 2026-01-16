import pandas as pd
from ml.model import load_model


def predict_probabilities(model, features_df):
    """
    Returns ML probabilities for each row
    """
    X = features_df.drop(columns=["date"], errors="ignore")
    probs = model.predict_proba(X)[:, 1]

    result = features_df.copy()
    result["ml_probability"] = probs

    return result
