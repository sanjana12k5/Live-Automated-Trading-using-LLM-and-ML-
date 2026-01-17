class MarketSimulator:
    def __init__(self, df):
        self.df = df.reset_index(drop=True)
        self.pointer = 0

    def has_next(self):
        return self.pointer < len(self.df)

    def next_candle(self):
        candle = self.df.iloc[self.pointer]
        self.pointer += 1
        return candle
