import joblib
from xgboost import XGBClassifier


MODEL_PATH = "ml/models/xgb_global_model.pkl"


def save_model(model):
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


def load_model():
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    return model
