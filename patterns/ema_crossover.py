import pandas as pd
from ta.trend import EMAIndicator

def detect_ema_crossover(df, fast_period=9, slow_period=15):
    """
    Detects moving average crossovers between a fast and slow EMA.
    Returns:
        "BULLISH", "BEARISH", or "NONE"
    """
    if len(df) < slow_period + 1:
        return "NONE"

    # Calculate EMAs
    fast_ema = EMAIndicator(close=df["close"], window=fast_period).ema_indicator()
    slow_ema = EMAIndicator(close=df["close"], window=slow_period).ema_indicator()

    # Get last two values to check for crossover
    fast_prev = fast_ema.iloc[-2]
    slow_prev = slow_ema.iloc[-2]
    
    fast_curr = fast_ema.iloc[-1]
    slow_curr = slow_ema.iloc[-1]

    if pd.isna(fast_curr) or pd.isna(slow_curr) or pd.isna(fast_prev) or pd.isna(slow_prev):
        return "NONE"

    # BULLISH Crossover: Fast was below (or equal) to Slow, now Fast is above Slow
    if fast_prev <= slow_prev and fast_curr > slow_curr:
        return "BULLISH"
    
    # BEARISH Crossover: Fast was above (or equal) to Slow, now Fast is below Slow
    if fast_prev >= slow_prev and fast_curr < slow_curr:
        return "BEARISH"

    return "NONE"
