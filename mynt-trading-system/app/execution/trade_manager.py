
import os
from signal import signal
import uuid
import pandas as pd


class TradeManager:

    FILE_PATH = "data/trades/trades.csv"

    @classmethod
    def save_trade(cls, signal):

        os.makedirs(
            "data/trades",
            exist_ok=True
        )


        trade_row = {
            
            "trade_id":
            str(uuid.uuid4()),

            "symbol":
            signal["symbol"],

            "signal_time":
            signal["signal_time"],

            "entry_time":
            signal["entry_time"],

            "entry_price":
            signal["entry_price"],

            "stop_loss":
            signal["stop_loss"],

            "quantity":
            signal["quantity"],

            "exit_time":
            "",

            "exit_price":
            "",

            "gross_pnl":
            0,

            "net_pnl":
            0,

            "exit_reason":
            "",

            "trade_status":
            "OPEN",

            "strategy_name":
            signal["strategy_name"]
        }



        if os.path.exists(cls.FILE_PATH):

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

        print(
            f"Trade Saved : "
            f"{trade_row['trade_id']}"
        )

        return trade_row
    
    @classmethod
    def update_stop_loss(
        cls,
        trade_id,
        new_sl
    ):

        df = pd.read_csv(
            cls.FILE_PATH
        )

        df.loc[
            df["trade_id"] == trade_id,
            "stop_loss"
        ] = new_sl

        df.to_csv(
            cls.FILE_PATH,
            index=False
        )

    @classmethod
    def get_all_trades(cls):

        if not os.path.exists(
            cls.FILE_PATH
        ):

            return pd.DataFrame()

        return pd.read_csv(
            cls.FILE_PATH
        )

    @classmethod
    def get_open_trades(cls):

        if not os.path.exists(
            cls.FILE_PATH
        ):

            return pd.DataFrame()

        df = pd.read_csv(
            cls.FILE_PATH
        )

        return df[
            df["trade_status"] == "OPEN"
        ]

    @classmethod
    def update_trade_status(
        cls,
        trade_id,
        status
    ):

        if not os.path.exists(
            cls.FILE_PATH
        ):

            return False

        df = pd.read_csv(
            cls.FILE_PATH
        )

        df.loc[
            df["trade_id"] == trade_id,
            "trade_status"
        ] = status

        df.to_csv(
            cls.FILE_PATH,
            index=False
        )

        return True

    

    @classmethod
    def close_trade(
        cls,
        trade_id,
        exit_time,
        exit_price,
        gross_pnl,
        net_pnl,
        exit_reason
    ):

        df = pd.read_csv(
            cls.FILE_PATH,
            dtype=str
        )

        mask = (
            df["trade_id"] == trade_id
        )

        df.loc[
            mask,
            "exit_time"
        ] = str(exit_time)

        df.loc[
            mask,
            "exit_price"
        ] = str(exit_price)

        df.loc[
            mask,
            "gross_pnl"
        ] = str(gross_pnl)

        df.loc[
            mask,
            "net_pnl"
        ] = str(net_pnl)

        df.loc[
            mask,
            "exit_reason"
        ] = exit_reason

        df.loc[
            mask,
            "trade_status"
        ] = "CLOSED"

        df.to_csv(
            cls.FILE_PATH,
            index=False
        )

        print(
            f"Trade Closed : {trade_id}"
        )