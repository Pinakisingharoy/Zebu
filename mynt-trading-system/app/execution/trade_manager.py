
# import os
# from signal import signal
# import uuid
# import pandas as pd


# class TradeManager:

#     FILE_PATH = "data/trades/trades.csv"

#     @classmethod
#     def save_trade(cls, signal):

#         os.makedirs(
#             "data/trades",
#             exist_ok=True
#         )


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

#             "stop_loss":
#             signal["stop_loss"],

#             "quantity":
#             signal["quantity"],

#             "exit_time":
#             "",

#             "exit_price":
#             "",

#             "gross_pnl":
#             0,

#             "net_pnl":
#             0,

#             "exit_reason":
#             "",

#             "trade_status":
#             "OPEN",

#             "strategy_name":
#             signal["strategy_name"]
#         }



#         if os.path.exists(cls.FILE_PATH):

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

#         print(
#             f"Trade Saved : "
#             f"{trade_row['trade_id']}"
#         )

#         return trade_row
    
#     @classmethod
#     def update_stop_loss(
#         cls,
#         trade_id,
#         new_sl
#     ):

#         df = pd.read_csv(
#             cls.FILE_PATH
#         )

#         df.loc[
#             df["trade_id"] == trade_id,
#             "stop_loss"
#         ] = new_sl

#         df.to_csv(
#             cls.FILE_PATH,
#             index=False
#         )
#         print(
#         f"SL Updated "
#         f"{trade_id} -> {new_sl}"
# )

#     @classmethod
#     def get_all_trades(cls):

#         if not os.path.exists(
#             cls.FILE_PATH
#         ):

#             return pd.DataFrame()

#         return pd.read_csv(
#             cls.FILE_PATH
#         )

#     @classmethod
#     def get_open_trades(cls):

#         if not os.path.exists(
#             cls.FILE_PATH
#         ):

#             return pd.DataFrame()

#         df = pd.read_csv(
#             cls.FILE_PATH
#         )

#         return df[
#             df["trade_status"] == "OPEN"
#         ]

#     @classmethod
#     def update_trade_status(
#         cls,
#         trade_id,
#         status
#     ):

#         if not os.path.exists(
#             cls.FILE_PATH
#         ):

#             return False

#         df = pd.read_csv(
#             cls.FILE_PATH
#         )

#         df.loc[
#             df["trade_id"] == trade_id,
#             "trade_status"
#         ] = status

#         df.to_csv(
#             cls.FILE_PATH,
#             index=False
#         )

#         return True

    

#     @classmethod
#     def close_trade(
#         cls,
#         trade_id,
#         exit_time,
#         exit_price,
#         gross_pnl,
#         net_pnl,
#         exit_reason
#     ):

#         df = pd.read_csv(
#             cls.FILE_PATH,
#             dtype=str
#         )

#         mask = (
#             df["trade_id"] == trade_id
#         )

#         df.loc[
#             mask,
#             "exit_time"
#         ] = str(exit_time)

#         df.loc[
#             mask,
#             "exit_price"
#         ] = str(exit_price)

#         df.loc[
#             mask,
#             "gross_pnl"
#         ] = str(gross_pnl)

#         df.loc[
#             mask,
#             "net_pnl"
#         ] = str(net_pnl)

#         df.loc[
#             mask,
#             "exit_reason"
#         ] = exit_reason

#         df.loc[
#             mask,
#             "trade_status"
#         ] = "CLOSED"

#         df.to_csv(
#             cls.FILE_PATH,
#             index=False
#         )

#         print(
#             f"Trade Closed : {trade_id}"
#         )

import pandas as pd
import uuid
import os
from datetime import datetime

class TradeManager:
    
    TRADE_FILE = "data/trades/trades.csv"
    
    @staticmethod
    def ensure_directory():
        os.makedirs(os.path.dirname(TradeManager.TRADE_FILE), exist_ok=True)
    
    @staticmethod
    def save_trade(signal):
        
        try:
            TradeManager.ensure_directory()
            
            trade_id = str(uuid.uuid4())
            
            trade = {
                "trade_id": trade_id,
                "symbol": signal["symbol"],
                "signal_time": signal["signal_time"],
                "entry_time": signal["entry_time"],
                "entry_price": float(signal["entry_price"]),
                "stop_loss": float(signal["stop_loss"]),
                "quantity": int(signal["quantity"]),
                "strategy_name": signal["strategy_name"],
                "trade_status": "OPEN",
                "exit_time": pd.NaT,  # Use pandas NaT for datetime
                "exit_price": None,
                "gross_pnl": None,
                "net_pnl": None,
                "exit_reason": ""  # Empty string instead of None
            }
            
            df = pd.DataFrame([trade])
            
            # Ensure correct dtypes
            df = df.astype({
                'trade_id': 'string',
                'symbol': 'string',
                'signal_time': 'datetime64[ns]',
                'entry_time': 'datetime64[ns]',
                'entry_price': 'float64',
                'stop_loss': 'float64',
                'quantity': 'int64',
                'strategy_name': 'string',
                'trade_status': 'string',
                'exit_time': 'datetime64[ns]',
                'exit_price': 'float64',
                'gross_pnl': 'float64',
                'net_pnl': 'float64',
                'exit_reason': 'string'  # String dtype for exit_reason
            }, errors='ignore')
            
            if os.path.exists(TradeManager.TRADE_FILE):
                existing = pd.read_csv(TradeManager.TRADE_FILE)
                # Ensure existing has same dtypes
                for col in df.columns:
                    if col in existing.columns:
                        existing[col] = existing[col].astype(df[col].dtype, errors='ignore')
                df = pd.concat([existing, df], ignore_index=True)
            
            df.to_csv(TradeManager.TRADE_FILE, index=False)
            
            return trade
            
        except Exception as e:
            print(f"Error saving trade: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_all_trades():
        
        try:
            if not os.path.exists(TradeManager.TRADE_FILE):
                return pd.DataFrame()
            
            df = pd.read_csv(TradeManager.TRADE_FILE)
            
            # Convert datetime columns
            for col in ["entry_time", "signal_time", "exit_time"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Ensure exit_reason is string
            if 'exit_reason' in df.columns:
                df['exit_reason'] = df['exit_reason'].fillna('').astype(str)
            
            return df
            
        except Exception as e:
            print(f"Error reading trades: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_open_trades():
        
        trades = TradeManager.get_all_trades()
        
        if trades.empty:
            return trades
        
        return trades[trades["trade_status"] == "OPEN"]
    
    @staticmethod
    def update_stop_loss(trade_id, new_sl):
        
        try:
            trades = TradeManager.get_all_trades()
            
            if trades.empty:
                return
            
            trades.loc[trades["trade_id"] == trade_id, "stop_loss"] = float(new_sl)
            
            trades.to_csv(TradeManager.TRADE_FILE, index=False)
            
        except Exception as e:
            print(f"Error updating stop loss: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def close_trade(trade_id, exit_time, exit_price, gross_pnl, net_pnl, exit_reason):
        
        try:
            trades = TradeManager.get_all_trades()
            
            if trades.empty:
                return
            
            # Ensure all values are properly typed
            trades.loc[trades["trade_id"] == trade_id, "exit_time"] = pd.to_datetime(exit_time)
            trades.loc[trades["trade_id"] == trade_id, "exit_price"] = float(exit_price)
            trades.loc[trades["trade_id"] == trade_id, "gross_pnl"] = float(gross_pnl)
            trades.loc[trades["trade_id"] == trade_id, "net_pnl"] = float(net_pnl)
            trades.loc[trades["trade_id"] == trade_id, "exit_reason"] = str(exit_reason)
            trades.loc[trades["trade_id"] == trade_id, "trade_status"] = "CLOSED"
            
            trades.to_csv(TradeManager.TRADE_FILE, index=False)
            
        except Exception as e:
            print(f"Error closing trade: {e}")
            import traceback
            traceback.print_exc()