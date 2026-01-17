import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class LiveMarket:
    def __init__(self, start_price=100.0):
        self.price = start_price
        self.data = []
        self.time = datetime.now()

        self.volatility = 0.002   # intraday vol
        self.trend_bias = np.random.choice([-1, 1]) * 0.0005

    def next_candle(self):
        # Regime shift occasionally
        if np.random.rand() < 0.03:
            self.trend_bias = np.random.choice([-1, 1]) * np.random.uniform(0.0003, 0.001)

        change = (
            self.trend_bias +
            np.random.normal(0, self.volatility)
        )

        open_price = self.price
        close_price = open_price * (1 + change)

        high = max(open_price, close_price) * (1 + np.random.uniform(0, 0.001))
        low = min(open_price, close_price) * (1 - np.random.uniform(0, 0.001))

        self.price = close_price
        self.time += timedelta(minutes=1)

        candle = {
            "date": self.time,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price,
            "volume": np.random.randint(1000, 5000),
        }

        self.data.append(candle)
        return candle

    def get_dataframe(self):
        return pd.DataFrame(self.data)
