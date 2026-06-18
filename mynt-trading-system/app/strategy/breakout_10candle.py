import pandas as pd

from app.strategy.base_strategy import BaseStrategy


class Breakout10Candle(BaseStrategy):

    STRATEGY_NAME = "10_CANDLE_BREAKOUT"

    def generate_signals(self, df):

        signals = []

        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)

        df["datetime"] = pd.to_datetime(
            df["datetime"]
        )

        # Need 10 previous candles
        # and 1 future candle for entry

        for i in range(10, len(df) - 1):

            previous_10 = df.iloc[i-10:i]

            highest_close = (
                previous_10["close"]
                .max()
            )

            signal_candle = df.iloc[i]

            signal_close = (
                signal_candle["close"]
            )

            # Rule 3

            if signal_close > highest_close:

                next_candle = df.iloc[i + 1]

                signals.append({

                    "symbol":
                    signal_candle["symbol"],

                    "signal_time":
                    signal_candle["datetime"],

                    "entry_time":
                    next_candle["datetime"],

                    "entry_price":
                    next_candle["open"],

                    "strategy_name":
                    self.STRATEGY_NAME
                })

        return signals