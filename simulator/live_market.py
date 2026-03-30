import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class LiveMarket:
    def __init__(self, start_price=100.0, start_time=None, dataframe=None):
        self.price = start_price
        self.data = []
        self.dataframe = dataframe
        self.current_step = 0
        
        if start_time:
            self.time = start_time
        elif dataframe is not None and not dataframe.empty:
            self.time = dataframe.iloc[0]["date"]
        else:
            now = datetime.now()
            self.time = now.replace(hour=9, minute=15, second=0, microsecond=0)

        self.volatility = 0.002   # intraday vol
        self.trend_bias = np.random.choice([-1, 1]) * 0.0005

    def next_candle(self):
        # HISTORICAL REPLAY
        if self.dataframe is not None:
            if self.current_step < len(self.dataframe):
                candle = self.dataframe.iloc[self.current_step].to_dict()
                self.price = candle["close"]
                self.time = candle["date"]
                self.data.append(candle)
                self.current_step += 1
                return candle
            else:
                # End of data, just return last candle or stop
                return self.data[-1]

        # REGULAR RANDOM GENERATION
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
