from data.processed.loader import load_stock
from features.feature_builder import build_features
from backtest.dataset_scan import scan_dataset
from ml.model import load_model
from ml.inference import predict_probabilities
from ml.ranking import  rank_trades_daily


def compare_ml_vs_rule(symbol="AAPL"):
    df = load_stock(symbol)

    # ---------- RULE TRADES ----------
    rule_trades = scan_dataset(df)

    # Map rule trades by date
    rule_map = {t["date"]: t for t in rule_trades}

    # ---------- ML TRADES ----------
    features = build_features(df)
    model = load_model()

    scored = predict_probabilities(model, features)
    from ml.ranking import rank_trades_daily

    ranked = rank_trades_daily(scored, top_k=1)


    # 🔥 attach price + signal from rule engine
    ml_trades = []
    for _, row in ranked.iterrows():
        trade_date = row["date"]
        if trade_date in rule_map:
            t = rule_map[trade_date]
            ml_trades.append({
                "date": trade_date,
                "price": t["price"],
                "signal": t["signal"],
                "ml_probability": row["ml_probability"],
                "atr": row["atr"]
            })


    return rule_trades, ml_trades
