
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
            print("No trades found")
            return

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%d-%m-%Y %H:%M:%S"
        )

        df["low"] = pd.to_numeric(df["low"])

        df["close"] = pd.to_numeric(df["close"])

        for _, trade in trades.iterrows():

            if trade["trade_status"] != "OPEN":
                continue

            entry_time = pd.to_datetime(
                trade["entry_time"]
            )

            entry_price = float(
                trade["entry_price"]
            )

            current_sl = float(
                trade["stop_loss"]
            )

            quantity = int(
                trade["quantity"]
            )

            future_candles = (
                df[
                    df["datetime"] > entry_time
                ]
                .copy()
                .reset_index(drop=True)
            )

            if len(future_candles) < 2:
                continue

            print("\n" + "=" * 50)
            print(
                f"Trade ID : {trade['trade_id']}"
            )
            print(
                f"Entry Price : {entry_price}"
            )
            print(
                f"Initial SL : {current_sl}"
            )
            print("=" * 50)

            for i in range(
                1,
                len(future_candles)
            ):

                previous_candle = (
                    future_candles.iloc[i - 1]
                )

                current_candle = (
                    future_candles.iloc[i]
                )

                previous_low = float(
                    previous_candle["low"]
                )

                # Trailing SL
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

                    print(
                        f"SL Updated -> {current_sl}"
                    )

                current_low = float(
                    current_candle["low"]
                )

                current_close = float(
                    current_candle["close"]
                )

                # Exit Logic
                if (
                    current_low <= current_sl
                    or
                    current_close <= current_sl
                ):

                    exit_price = current_sl

                    gross_pnl = (
                        exit_price -
                        entry_price
                    ) * quantity

                    net_pnl = (
                        gross_pnl -
                        ExitEngine.BROKERAGE
                    )

                    TradeManager.close_trade(
                        trade["trade_id"],
                        current_candle["datetime"],
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