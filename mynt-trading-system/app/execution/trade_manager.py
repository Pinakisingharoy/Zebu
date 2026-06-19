# import os
# import uuid

# import pandas as pd


# class TradeManager:

#     FILE_PATH = (
#         "data/trades/trades.csv"
#     )

#     @classmethod
#     def save_trade(
#         cls,
#         trade
#     ):

#         os.makedirs(
#             "data/trades",
#             exist_ok=True
#         )

#         # trade_row = {

#         #     "trade_id":
#         #     str(uuid.uuid4()),

#         #     "symbol":
#         #     trade["symbol"],

#         #     "signal_time":
#         #     trade["signal_time"],

#         #     "entry_time":
#         #     trade["entry_time"],

#         #     "entry_price":
#         #     trade["entry_price"],

#         #     "quantity":
#         #     1,

#         #     "strategy_name":
#         #     trade["strategy_name"]
#         # }

#         trade_row = {

#             "trade_id":
#             str(uuid.uuid4()),

#             "symbol":
#             signal["symbol"],

#             "signal_time":
#             signal["signal_time"],

#             "entry_time":
#             signal["entry_time"],

#             "entry_price":
#             signal["entry_price"],

#             # NEW FIELD
#             "stop_loss":
#             signal["stop_loss"],

#             "quantity":
#             1,

#             "strategy_name":
#             signal["strategy_name"]
#         }



#         if os.path.exists(
#             cls.FILE_PATH
#         ):

#             df = pd.read_csv(
#                 cls.FILE_PATH
#             )

#             df = pd.concat(
#                 [
#                     df,
#                     pd.DataFrame(
#                         [trade_row]
#                     )
#                 ],
#                 ignore_index=True
#             )

#         else:

#             df = pd.DataFrame(
#                 [trade_row]
#             )

#         df.to_csv(
#             cls.FILE_PATH,
#             index=False
#         )

#         return trade_row

import os
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

        # trade_row = {

        #     "trade_id":
        #     str(uuid.uuid4()),

        #     "symbol":
        #     signal["symbol"],

        #     "signal_time":
        #     signal["signal_time"],

        #     "entry_time":
        #     signal["entry_time"],

        #     "entry_price":
        #     signal["entry_price"],

        #     "stop_loss":
        #     signal["stop_loss"],

        #     "quantity":
        #     1,

        #     "strategy_name":
        #     signal["strategy_name"],

        #     "trade_status":
        #     "OPEN"
        # }

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

            "strategy_name":
            signal["strategy_name"],

            "trade_status":
            "OPEN"
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