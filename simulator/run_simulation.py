from data.processed.loader import load_stock
from simulator.market_simulator import MarketSimulator
from simulator.portfolio import Portfolio
from simulator.trade_engine import check_exit

from features.feature_builder import build_features
from ml.model import load_model
from ml.inference import predict_probabilities
from ml.ranking import rank_trades_daily


def run_simulation(symbol="AAPL"):
    df = load_stock(symbol)
    model = load_model()

    simulator = MarketSimulator(df)
    portfolio = Portfolio()

    history = []

    # ----------------------------
    # CONTROLS (IMPORTANT)
    # ----------------------------
    MIN_ML_PROB = 0.7
    COOLDOWN = 10          # candles
    last_trade_index = -999

    while simulator.has_next():
        candle = simulator.next_candle()

        # progress heartbeat
        if simulator.pointer % 50 == 0:
            print(f"Processed candle {simulator.pointer}/{len(df)}")

        history.append(candle)

        # wait until enough candles
        if len(history) < 100:
            continue

        hist_df = df.iloc[: len(history)]

        # ----------------------------
        # FEATURE BUILD (LAST ONLY)
        # ----------------------------
        features = build_features(hist_df, last_only=True)

        if features.empty:
            continue

        scored = predict_probabilities(model, features)

        if scored.empty:
            continue

        ranked = rank_trades_daily(scored, top_k=1)

        # ----------------------------
        # OPEN NEW TRADE (CONTROLLED)
        # ----------------------------
        for _, row in ranked.iterrows():

            # ML confidence filter
            if row["ml_probability"] < MIN_ML_PROB:
                continue

            # only act on current candle
            if row["date"] != candle["date"]:
                continue

            # single position rule
            if portfolio.positions:
                continue

            # cooldown rule
            if simulator.pointer - last_trade_index < COOLDOWN:
                continue

            trade = {
                "date": row["date"],
                "price": row["close"],
                "signal": "BUY",   # (SELL later when you add shorting)
                "ml_probability": row["ml_probability"],
                "atr": row["atr"],
                "position_size": row["ml_probability"] / row["atr"],
                "sl": row["close"] * (1 - 0.02),
                "tp": row["close"] * (1 + 0.04),
            }

            portfolio.open_position(trade)
            last_trade_index = simulator.pointer

        # ----------------------------
        # MANAGE OPEN POSITIONS
        # ----------------------------
        for trade in portfolio.positions.copy():
            exit_price, reason = check_exit(trade, candle)
            if exit_price:
                portfolio.close_position(
                    trade,
                    exit_price,
                    candle["date"],
                    reason
                )

    return portfolio
