from data.processed.loader import load_stock
from features.feature_builder import build_features
from ml.model import load_model
from ml.inference import predict_probabilities
from ml.ranking import rank_trades


def run_ml_pipeline(symbol, ranking_method="percentile", ranking_value=99.5):
    df = load_stock(symbol)

    features = build_features(df)
    model = load_model()

    scored = predict_probabilities(model, features)

    ranked = rank_trades(
        scored,
        method=ranking_method,
        value=ranking_value
    )

    return ranked
