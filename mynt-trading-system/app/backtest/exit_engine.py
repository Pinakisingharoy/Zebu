import pandas as pd

from app.execution.trade_manager import (
    TradeManager
)

from app.strategy.trailing_sl import (
    TrailingSL
)


class ExitEngine:

    BROKERAGE = 40

    @staticmethod
    def process_trades(df):

        trades = TradeManager.get_all_trades()

        if trades.empty:
            return

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%d-%m-%Y %H:%M:%S"
        )

        for _, trade in trades.iterrows():

            if trade["trade_status"] != "OPEN":
                continue

            entry_time = pd.to_datetime(
                trade["entry_time"]
            )

            entry_price = float(
                trade["entry_price"]
            )

            stop_loss = float(
                trade["stop_loss"]
            )

            quantity = int(
                trade["quantity"]
            )

            future_candles = df[
                df["datetime"] > entry_time
            ]

            # ---------------------
            # Initial SL
            # ---------------------

            current_sl = stop_loss

            # Previous candle low
            previous_low = stop_loss

            # ---------------------
            # Process future candles
            # ---------------------

            for _, candle in future_candles.iterrows():

                candle_low = float(
                    candle["low"]
                )

                candle_close = float(
                    candle["close"]
                )

                # ---------------------
                # Update Trailing SL
                # Using PREVIOUS candle low
                # ---------------------

                new_sl = (
                    TrailingSL.update_sl(
                        current_sl,
                        previous_low
                    )
                )

                if new_sl > current_sl:

                    current_sl = new_sl

                    TradeManager.update_stop_loss(
                        trade["trade_id"],
                        current_sl
                    )

                # ---------------------
                # Exit Condition
                # ---------------------

                if (
                    candle_low <= current_sl
                    or
                    candle_close <= current_sl
                ):

                    exit_price = current_sl

                    gross_pnl = (
                        (
                            exit_price
                            - entry_price
                        )
                        * quantity
                    )

                    net_pnl = (
                        gross_pnl
                        - ExitEngine.BROKERAGE
                    )

                    TradeManager.close_trade(
                        trade["trade_id"],
                        candle["datetime"],
                        exit_price,
                        gross_pnl,
                        net_pnl,
                        "TRAILING_SL_HIT"
                    )

                    print(
                        f"Trade Closed -> "
                        f"{trade['trade_id']}"
                    )

                    break

                # ---------------------
                # Save current candle low
                # for next candle trail
                # ---------------------

                previous_low = candle_low