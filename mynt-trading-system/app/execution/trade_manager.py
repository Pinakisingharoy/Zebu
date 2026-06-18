import os
import uuid

import pandas as pd


class TradeManager:

    FILE_PATH = (
        "data/trades/trades.csv"
    )

    @classmethod
    def save_trade(
        cls,
        trade
    ):

        os.makedirs(
            "data/trades",
            exist_ok=True
        )

        trade_row = {

            "trade_id":
            str(uuid.uuid4()),

            "symbol":
            trade["symbol"],

            "signal_time":
            trade["signal_time"],

            "entry_time":
            trade["entry_time"],

            "entry_price":
            trade["entry_price"],

            "quantity":
            1,

            "strategy_name":
            trade["strategy_name"]
        }

        if os.path.exists(
            cls.FILE_PATH
        ):

            df = pd.read_csv(
                cls.FILE_PATH
            )

            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [trade_row]
                    )
                ],
                ignore_index=True
            )

        else:

            df = pd.DataFrame(
                [trade_row]
            )

        df.to_csv(
            cls.FILE_PATH,
            index=False
        )

        return trade_row