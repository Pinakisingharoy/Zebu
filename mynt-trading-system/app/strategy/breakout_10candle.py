# import pandas as pd

# from app.strategy.base_strategy import BaseStrategy


# class Breakout10Candle(BaseStrategy):

#     STRATEGY_NAME = "10_CANDLE_BREAKOUT"

#     def generate_signals(self, df):

#         signals = []

#         df["datetime"] = pd.to_datetime(
#             df["datetime"],
#             format="%d-%m-%Y %H:%M:%S"
#         )

#         df["open"] = pd.to_numeric(df["open"])
#         df["high"] = pd.to_numeric(df["high"])
#         df["low"] = pd.to_numeric(df["low"])
#         df["close"] = pd.to_numeric(df["close"])

#         df = (
#             df
#             .sort_values("datetime")
#             .reset_index(drop=True)
#         )

#         # Need:
#         # 10 candles history
#         # 1 signal candle
#         # 1 entry candle

#         if len(df) < 12:
#             return signals

#         for i in range(11, len(df)):

#             # --------------------------------
#             # Previous 10 completed candles
#             # --------------------------------

#             previous_10 = df.iloc[i - 11:i - 1]

#             highest_close = (
#                 previous_10["close"]
#                 .max()
#             )

#             # --------------------------------
#             # Signal Candle
#             # --------------------------------

#             signal_candle = df.iloc[i - 1]

#             signal_close = float(
#                 signal_candle["close"]
#             )

#             # --------------------------------
#             # Entry Candle
#             # --------------------------------

#             entry_candle = df.iloc[i]

#             # --------------------------------
#             # Breakout Condition
#             # --------------------------------

#             if signal_close > highest_close:

#                 signal = {

#                     "symbol":
#                     signal_candle["symbol"],

#                     "signal_time":
#                     signal_candle["datetime"],

#                     "signal_close":
#                     signal_close,

#                     "highest_close":
#                     highest_close,

#                     "entry_time":
#                     entry_candle["datetime"],

#                     "entry_price":
#                     float(
#                         entry_candle["open"]
#                     ),

#                     "stop_loss":
#                     float(
#                         signal_candle["low"]
#                     ),

#                     "quantity":
#                     1,

#                     "strategy_name":
#                     self.STRATEGY_NAME
#                 }

#                 signals.append(signal)

#                 # break

#         return signals



import pandas as pd

from app.strategy.base_strategy import (
    BaseStrategy
)


class Breakout10Candle(BaseStrategy):

    STRATEGY_NAME = "10_CANDLE_BREAKOUT"

    def generate_signals(self, df):

        signals = []

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%d-%m-%Y %H:%M:%S"
        )

        df["open"] = pd.to_numeric(df["open"])
        df["high"] = pd.to_numeric(df["high"])
        df["low"] = pd.to_numeric(df["low"])
        df["close"] = pd.to_numeric(df["close"])

        df = (
            df
            .sort_values("datetime")
            .reset_index(drop=True)
        )

        # -------------------------
        # Create Trading Date
        # -------------------------

        df["trade_date"] = (
            df["datetime"]
            .dt.date
        )

        # -------------------------
        # Process Day Wise
        # -------------------------

        for trade_date, day_df in df.groupby(
            "trade_date"
        ):

            day_df = (
                day_df
                .sort_values("datetime")
                .reset_index(drop=True)
            )

            # Need:
            # 10 candles history
            # 1 signal candle
            # 1 entry candle

            if len(day_df) < 12:
                continue

            # -------------------------
            # Start from 11th index
            # First possible signal:
            # 09:25
            # First entry:
            # 09:26
            # -------------------------

            for i in range(
                11,
                len(day_df)
            ):

                # -------------------------
                # Previous 10 completed candles
                # -------------------------

                previous_10 = day_df.iloc[
                    i - 11:i - 1
                ]

                highest_close = (
                    previous_10["close"]
                    .max()
                )

                # -------------------------
                # Signal Candle
                # -------------------------

                signal_candle = (
                    day_df.iloc[i - 1]
                )

                signal_close = float(
                    signal_candle["close"]
                )

                signal_time = (
                    signal_candle["datetime"]
                    .time()
                )

                # -------------------------
                # No signal before 09:25
                # -------------------------

                if signal_time < pd.to_datetime(
                    "09:25:00"
                ).time():
                    continue

                # -------------------------
                # Entry Candle
                # -------------------------

                entry_candle = (
                    day_df.iloc[i]
                )

                # -------------------------
                # Breakout Condition
                # -------------------------

                if signal_close > highest_close:

                    signal = {

                        "symbol":
                        signal_candle["symbol"],

                        "signal_time":
                        signal_candle["datetime"],

                        "signal_close":
                        signal_close,

                        "highest_close":
                        highest_close,

                        "entry_time":
                        entry_candle["datetime"],

                        "entry_price":
                        float(
                            entry_candle["open"]
                        ),

                        # Previous Candle Low
                        "stop_loss":
                        float(
                            signal_candle["low"]
                        ),

                        "quantity":
                        1,

                        "strategy_name":
                        self.STRATEGY_NAME
                    }

                    signals.append(signal)

        return signals