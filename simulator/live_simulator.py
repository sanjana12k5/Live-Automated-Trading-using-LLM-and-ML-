import time
import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

from simulator.live_market import LiveMarket
from simulator.live_plotter import LivePlotter
from simulator.trade_engine import check_exit
from simulator.portfolio import Portfolio
# test change
from patterns.candlestick_patterns import (
    detect_hammer,
    detect_inverted_hammer,
    detect_engulfing,
    detect_morning_star,
    detect_evening_star,
    detect_bullish_harami,
    detect_bearish_harami,
    detect_three_white_soldiers,
    detect_three_black_crows,
    detect_bullish_breakout,
    detect_bearish_breakdown,
    detect_shooting_star,
)
from patterns.structure import detect_swings, label_structure
from patterns.trend import detect_trend, detect_choch
from patterns.fib.confluence import fib_confluence
from patterns.chart_patterns import detect_double_bottom, detect_double_top
from patterns.ema_crossover import detect_ema_crossover
from execution.signal_engine import generate_signal

from ml.model import load_model
from ml.inference import predict_probabilities


def run_live_simulation(
    candles=350,
    start_price=100.0,
    symbol="SIMULATED",
    enable_plot=True,
    strategy_mode="DEFAULT"
):
    print(f"Starting LIVE simulation: {symbol} @ {start_price} (Mode: {strategy_mode})")

    # OPTIMIZED CONFIGURATION (Aggressive Long-Only)
    PATTERN_CONFIG = {
        "Double Bottom":     {"thresh": 0.40, "min_ml": 0.55}, # Proven Winner
        "Double Top":        {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "Evening Star":      {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "3 White Soldiers":  {"thresh": 0.40, "min_ml": 0.50}, # Aggressive Volume
        "Hammer":            {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "Bearish Engulfing": {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "Inverted Hammer":   {"thresh": 0.40, "min_ml": 0.10}, 
        "Bullish Engulfing": {"thresh": 0.30, "min_ml": 0.10}, # ULTRA AGGRESSIVE (Catch 0.34 scores)
        "3 Black Crows":     {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "Shooting Star":     {"thresh": 0.65, "min_ml": 0.55}, # Defensive
        "Morning Star":      {"thresh": 0.35, "min_ml": 0.35}, # VERY AGGRESSIVE
    }
    
    DEFAULT_CONFIG = {"thresh": 0.55, "min_ml": 0.50}

    from data.processed.loader import load_stock

    # ---------- INIT ----------
    if symbol != "SIMULATED":
        print(f"Loading historical data for {symbol}...")
        history_df = load_stock(symbol)
        start_price = history_df.iloc[0]["close"]
        market = LiveMarket(start_price=start_price, dataframe=history_df)
        candles = len(history_df) # Override candles count
    else:
        market = LiveMarket(start_price=start_price)
        
    plotter = LivePlotter(symbol=symbol) if enable_plot else None
    portfolio = Portfolio()
    model = load_model()

    MIN_ML_PROB = 0.6      # ML Enabled to reduce losses
    COOLDOWN = 1           # Aggressive Re-entry
    last_trade_step = -999

    # ---------- LIVE LOOP ----------
    for step in range(candles):
        candle = market.next_candle()
        df = market.get_dataframe()

        if step % 50 == 0:
            print(f"Processed candle {step}/{candles}")

        # ---- Minimum candles ----
        if len(df) < 20:
            if plotter:
                plotter.update(df, portfolio.trade_log, portfolio.cash)
            time.sleep(0.05)
            continue

        # ---------- PATTERN DETECTION ----------
        swings = detect_swings(df)
        if len(swings) < 5:
            continue

        structure = label_structure(swings)
        trend = detect_trend(structure)
        choch = detect_choch(structure)
        fib = fib_confluence(swings, df)

        db = detect_double_bottom(structure)
        dt = detect_double_top(structure)

        # Candlestick Patterns
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        last3 = df.iloc[-3:].to_dict("records")

        hammer = detect_hammer(curr)
        inv_hammer = detect_inverted_hammer(curr)
        bull_engulf, bear_engulf = detect_engulfing(prev, curr)
        morning_star = detect_morning_star(last3)
        bull_harami = detect_bullish_harami(prev, curr)
        three_white = detect_three_white_soldiers(last3)
        bull_breakout = detect_bullish_breakout(df)

        shooting_star = detect_shooting_star(curr)
        evening_star = detect_evening_star(last3)
        bear_harami = detect_bearish_harami(prev, curr)
        three_black = detect_three_black_crows(last3)
        bear_breakdown = detect_bearish_breakdown(df)


        signal_data = generate_signal(
            trend=trend,
            choch=choch,
            hammer=hammer,
            inv_hammer=inv_hammer,
            bull_engulf=bull_engulf,
            morning_star=morning_star,
            bull_harami=bull_harami,
            three_white=three_white,
            bull_breakout=bull_breakout,
            bear_engulf=bear_engulf,
            shooting_star=shooting_star,
            evening_star=evening_star,
            bear_harami=bear_harami,
            three_black=three_black,
            bear_breakdown=bear_breakdown,
            fib=fib,
            double_bottom=db,
            double_top=dt
        )
        
        signal = signal_data["signal"]
        pattern_name = signal_data.get("reason", "Unknown Pattern")

        if signal == "NO_TRADE":
            signal = None

        # ---------- FEATURE ENGINEERING & ML ----------
        ml_prob = 0.5  # Default neutral if not enough data
        
        if len(df) >= 120:
            try:
                # 1. Calculate Indicators on the fly
                # We need a stable window for ATR/RSI, so take more history
                calc_df = df.iloc[-150:].copy() 
                
                atr = AverageTrueRange(
                    high=calc_df["high"], low=calc_df["low"], close=calc_df["close"], window=14
                ).average_true_range()
                
                rsi = RSIIndicator(calc_df["close"], window=14).rsi() # Volume Ratio
                
                vol_sma = calc_df["volume"].rolling(20).mean().iloc[-1]
                vol_ratio = (curr["volume"] / vol_sma) if vol_sma > 0 else 1.0
                
                # 2. Construct Feature Vector (Must match training!)
                # Mappings: UPTREND=1, DOWNTREND=-1, else 0
                trend_val = 1 if trend == "UPTREND" else -1 if trend == "DOWNTREND" else 0
                
                features = {
                    "close": curr["close"],
                    
                    # Trend / Structure
                    "trend": trend_val,
                    "choch": int(choch),
                    
                    # Fibonacci
                    "fib_confluence": int(fib["fib_confluence"]),
                    "fib_strength": fib["confidence"],
                    
                    # Bullish patterns
                    "hammer": int(hammer),
                    "inv_hammer": int(inv_hammer),
                    "bull_engulf": int(bull_engulf),
                    "morning_star": int(morning_star),
                    "bull_harami": int(bull_harami),
                    "three_white": int(three_white),
                    "bull_breakout": int(bull_breakout),
                    
                    # Bearish patterns
                    "bear_engulf": int(bear_engulf),
                    "shooting_star": int(shooting_star),
                    "evening_star": int(evening_star),
                    "bear_harami": int(bear_harami),
                    "three_black": int(three_black),
                    "bear_breakdown": int(bear_breakdown),
                    
                    # Indicators
                    "atr": atr.iloc[-1],
                    "rsi": rsi.iloc[-1],
                    "volume_ratio": vol_ratio,
                }
                
                # Prepare DataFrame for inference
                features_df = pd.DataFrame([features])
                
                scored = predict_probabilities(model, features_df)
                if not scored.empty:
                    raw_prob = float(scored["ml_probability"].iloc[0])
                    
                    # 3. Calibrate / Normalize Probability
                    # The model is extremely conservative on simulated data (often < 0.05).
                    # We map the 0.00-0.10 range to 0.00-0.60 to make it usable.
                    if raw_prob < 0.10:
                        ml_prob = raw_prob * 6.0  # Scale up low probs
                    else:
                        ml_prob = raw_prob
                    
                    ml_prob = min(ml_prob, 0.95) # Cap at 0.95
            except Exception as e:
                print(f"[ML Warn] {e}")
                ml_prob = 0.5

        # ---------- SCORING & EXECUTION ----------
        # Weighted Score: 40% Pattern Confidence + 60% ML Probability
        signal_conf = signal_data.get("confidence", 0.0)
        final_score = (signal_conf * 0.4) + (ml_prob * 0.6)
        
        # ---------- DYNAMIC THRESHOLD LOOKUP ----------
        config = PATTERN_CONFIG.get(pattern_name, DEFAULT_CONFIG)
        THRESHOLD = config["thresh"]
        min_ml_prob = config["min_ml"]

        # FILTER: ML Probability Check
        if ml_prob < min_ml_prob:
            # print(f"[FILTER] {pattern_name} rejected (ML={ml_prob:.2f} < {min_ml_prob})") 
            continue

        # TREND FILTER: Allow counter-trend if Score is strong (e.g. > 0.60)
        # For 'Double Bottom' with low thresh (0.40), we might want trend alignment?
        # The analysis said 0.40/0.55 was best for DB. Let's trust the analysis.
        trend_aligned = False
        if signal == "BUY" and (trend == "UPTREND" or choch):
            trend_aligned = True
        # SELL logic removed for Long-Only optimization
            
        # ENTRY CONDITION
        # Allow if score meets threshold AND (Aligned OR Strong Score)
        # With optimized thresholds, we can trust the threshold itself more.
        is_valid_entry = (final_score >= THRESHOLD)

        if strategy_mode == "EMA_ONLY":
            crossover = detect_ema_crossover(df)
            if crossover == "BULLISH": signal = "BUY"
            elif crossover == "BEARISH": signal = "SELL"
            else: signal = None
            
            pattern_name = "EMA_9x15_Cross"
            final_score = 1.0
            ml_prob = 1.0
            is_valid_entry = (signal is not None)
            allow_short = True
        elif strategy_mode == "COMBINED":
            crossover = detect_ema_crossover(df)
            ema_signal = None
            if crossover == "BULLISH": ema_signal = "BUY"
            elif crossover == "BEARISH": ema_signal = "SELL"

            if ema_signal and is_valid_entry and signal == ema_signal:
                pattern_name = f"{pattern_name} + EMA Cross"
                final_score = min(1.0, final_score + 0.2)
            elif ema_signal:
                signal = ema_signal
                pattern_name = "EMA_9x15_Cross"
                final_score = 0.8
                is_valid_entry = True
            
            allow_short = True
        else:
            allow_short = False

        if (
            (signal == "BUY" or (allow_short and signal == "SELL"))
            and not portfolio.has_open_position()
            and is_valid_entry
            and step - last_trade_step >= COOLDOWN
        ):
            price = curr["close"]

            # DYNAMIC SL / TP (ATR Based for Daily/Intraday adaptability)
            # Try to use ATR from features, else estimate 1.5% volatility
            atr_val = float(features["atr"]) if "features" in locals() and "atr" in features else price * 0.015
            
            # SL = 1.0 ATR, TP = 2.0 ATR (Swing Settings)
            sl_dist = atr_val * 1.0
            tp_dist = atr_val * 2.0

            trade = {
                "entry_date": curr["date"],
                "entry_price": price,
                "signal": signal,
                "confidence": ml_prob,
                "pattern": pattern_name,
                "score": final_score,
                "ml_prob": ml_prob,

                "sl": price - sl_dist if signal == "BUY" else price + sl_dist,
                "tp": price + tp_dist if signal == "BUY" else price - tp_dist,
            }

            portfolio.open_position(trade)
            last_trade_step = step

            print(
                f"💡 [SUGGESTION] {signal} @ {price:.2f} | "
                f"Reason: {pattern_name} | Score={final_score:.2f} | "
                f"SL: {trade['sl']:.2f} | TP: {trade['tp']:.2f}"
            )
        elif signal and not portfolio.has_open_position():
            # Log rejected trade for debugging
            print(f"[REJECT] {signal} | {pattern_name} | Score={final_score:.2f} (ML={ml_prob:.2f})")

        # ---------- MANAGE OPEN TRADES (TRAILING STOP) ----------
        for trade in portfolio.positions.copy():
            # 0. Opposite Crossover Exit (For EMA)
            forced_exit = False
            exit_reason = ""
            if strategy_mode in ["EMA_ONLY", "COMBINED"]:
                crossover = detect_ema_crossover(df)
                if trade["signal"] == "BUY" and crossover == "BEARISH":
                    forced_exit = True
                    exit_reason = "Opposite Crossover"
                elif trade["signal"] == "SELL" and crossover == "BULLISH":
                    forced_exit = True
                    exit_reason = "Opposite Crossover"

            # 1. Trailing Stop / Breakeven Logic
            current_price = candle["close"]
            entry_price = trade["entry_price"]
            
            # If trade is > 0.25% in profit, move SL to Breakeven (+0.05% to cover fees)
            # STRICT RISK MANAGEMENT to balance aggressive entry
            if trade["signal"] == "BUY":
                if current_price >= entry_price * 1.0025:
                    new_sl = entry_price * 1.0005
                    if new_sl > trade["sl"]:
                        trade["sl"] = new_sl
                        # print(f"  [MGMT] Moved SL to BE: {new_sl:.2f}")
            elif trade["signal"] == "SELL":
                if current_price <= entry_price * 0.9975:
                    new_sl = entry_price * 0.9995
                    if new_sl < trade["sl"]:
                        trade["sl"] = new_sl
                        # print(f"  [MGMT] Moved SL to BE: {new_sl:.2f}")

            # 2. Check Hit
            if forced_exit:
                exit_price = current_price
                reason = exit_reason
            else:
                exit_price, reason = check_exit(trade, candle)
                
            if exit_price is not None:
                portfolio.close_position(
                    trade,
                    exit_price,
                    candle["date"],
                    reason
                )

                # last_trade_step = step  # REMOVED to allow immediate re-entry

                pnl = (exit_price - entry_price) * (1 if trade["signal"] == "BUY" else -1)
                result_str = "PROFIT" if pnl > 0 else "LOSS"
                print(
                    f"✅ [RESULT] Closed {trade['signal']} | "
                    f"Exit={exit_price:.2f} | Reason: {reason} | PnL: ${pnl:.2f} ({result_str})"
                )

        # ---------- LIVE VISUAL ----------
        if plotter:
            plotter.update(df, portfolio.trade_log, portfolio.cash)
            # time.sleep(0.001) # Fast mode
            time.sleep(0.05)    # Normal mode for visual

    # ---------- SUMMARY ----------
    print("\n" + "="*40)
    print("       SIMULATION PERFORMANCE REPORT       ")
    print("="*40)
    print(f"Final Capital: ${portfolio.cash:.2f}")
    print(f"Total Return : ${portfolio.cash - 100000:.2f} ({(portfolio.cash - 100000)/1000:.2f}%)")
    print(f"Total Trades : {len(portfolio.trade_log)}")

    if portfolio.trade_log:
        wins = [t for t in portfolio.trade_log if t["pnl"] > 0]
        losses = [t for t in portfolio.trade_log if t["pnl"] <= 0]
        
        win_rate = (len(wins) / len(portfolio.trade_log)) * 100
        avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0.0
        avg_loss = sum(t["pnl"] for t in losses) / len(losses) if losses else 0.0
        
        print(f"Win Rate     : {win_rate:.2f}%")
        print(f"Avg Win      : ${avg_win:.2f}")
        print(f"Avg Loss     : ${avg_loss:.2f}")
        print("-" * 40)
        
        # Pattern Stats
        print("\nPerformance by Pattern:")
        from collections import defaultdict
        pattern_stats = defaultdict(lambda: {"count": 0, "pnl": 0.0})
        
        for t in portfolio.trade_log:
            pat = t.get("pattern", "Unknown")
            pattern_stats[pat]["count"] += 1
            pattern_stats[pat]["pnl"] += t["pnl"]
            
        for pat, stats in pattern_stats.items():
            print(f"{pat:<20} | Count: {stats['count']:<3} | PnL: ${stats['pnl']:.2f}")

    print("="*40 + "\n")

    return portfolio
