import time

from simulator.live_market import LiveMarket
from simulator.live_plotter import LivePlotter
from simulator.trade_engine import check_exit
from simulator.portfolio import Portfolio

from patterns.candlestick_patterns import (
    detect_hammer,
    detect_engulfing,
    detect_three_white_soldiers,
    detect_three_black_crows,
)

from ml.model import load_model
from ml.inference import predict_probabilities


def run_live_simulation(
    candles=500,
    start_price=100.0,
    symbol="SIMULATED"
):
    print(f"Starting LIVE simulation: {symbol} @ {start_price}")

    market = LiveMarket(start_price=start_price)
    plotter = LivePlotter(symbol=symbol)
    portfolio = Portfolio()
    model = load_model()

    MIN_ML_PROB = 0.55  # ML = confirmation only

    for step in range(candles):
        candle = market.next_candle()
        df = market.get_dataframe()

        if step % 50 == 0:
            print(f"Processed candle {step}/{candles}")

        if len(df) < 5:
            plotter.update(df, portfolio.trade_log, portfolio.cash)
            time.sleep(0.05)
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]
        last3 = df.iloc[-3:].to_dict("records")

        bull_engulf, bear_engulf = detect_engulfing(prev, curr)
        hammer = detect_hammer(curr)
        three_white = detect_three_white_soldiers(last3)
        three_black = detect_three_black_crows(last3)

        signal = None
        pattern_name = None

        if hammer or bull_engulf or three_white:
            signal = "BUY"
            pattern_name = "Bullish Pattern"

        elif bear_engulf or three_black:
            signal = "SELL"
            pattern_name = "Bearish Pattern"

        # ---- ML CONFIRMATION (SAFE) ----
        ml_prob = 1.0
        if signal and len(df) >= 120:
            try:
                features = df.tail(120).copy()
                scored = predict_probabilities(model, features)
                if not scored.empty:
                    ml_prob = scored["ml_probability"].iloc[-1]
            except Exception:
                ml_prob = 1.0

        # ---- OPEN TRADE ----
        if (
            signal
            and not portfolio.has_open_position()
            and ml_prob >= MIN_ML_PROB
        ):
            price = curr["close"]

            trade = {
                "entry_date": curr["date"],
                "entry_price": price,
                "signal": signal,
                "confidence": ml_prob,
                "pattern": pattern_name,
                "sl": price * (0.997 if signal == "BUY" else 1.003),
                "tp": price * (1.006 if signal == "BUY" else 0.994),
            }

            portfolio.open_position(trade)

            print(
                f"[OPEN] {trade['signal']} @ {price:.2f} | "
                f"{pattern_name} | ML={ml_prob:.2f}"
            )

        # ---- MANAGE TRADES ----
        for trade in portfolio.positions.copy():
            exit_price, reason = check_exit(trade, candle)
            if exit_price is not None:
                portfolio.close_position(
                    trade, exit_price, candle["date"], reason
                )

                print(
                    f"[CLOSE] {trade['signal']} | "
                    f"Exit={exit_price:.2f} | {reason}"
                )

        plotter.update(df, portfolio.trade_log, portfolio.cash)
        time.sleep(0.05)

    print("\nSimulation finished")
    print("Final capital:", portfolio.cash)
    print("Total trades:", len(portfolio.trade_log))

    return portfolio
