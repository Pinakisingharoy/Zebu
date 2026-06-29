
# import pandas as pd
# import uuid
# import os
# from datetime import datetime

# class TradeManager:
    
#     TRADE_FILE = "data/trades/trades.csv"
    
#     @staticmethod
#     def ensure_directory():
#         os.makedirs(os.path.dirname(TradeManager.TRADE_FILE), exist_ok=True)
    
#     @staticmethod
#     def save_trade(signal):
        
#         try:
#             TradeManager.ensure_directory()
            
#             trade_id = str(uuid.uuid4())
            
#             trade = {
#                 "trade_id": trade_id,
#                 "symbol": signal["symbol"],
#                 "signal_time": signal["signal_time"],
#                 "entry_time": signal["entry_time"],
#                 "entry_price": float(signal["entry_price"]),
#                 "stop_loss": float(signal["stop_loss"]),
#                 "quantity": int(signal["quantity"]),
#                 "strategy_name": signal["strategy_name"],
#                 "trade_status": "OPEN",
#                 "exit_time": pd.NaT,  # Use pandas NaT for datetime
#                 "exit_price": None,
#                 "gross_pnl": None,
#                 "net_pnl": None,
#                 "exit_reason": ""  # Empty string instead of None
#             }
            
#             df = pd.DataFrame([trade])
            
#             # Ensure correct dtypes
#             df = df.astype({
#                 'trade_id': 'string',
#                 'symbol': 'string',
#                 'signal_time': 'datetime64[ns]',
#                 'entry_time': 'datetime64[ns]',
#                 'entry_price': 'float64',
#                 'stop_loss': 'float64',
#                 'quantity': 'int64',
#                 'strategy_name': 'string',
#                 'trade_status': 'string',
#                 'exit_time': 'datetime64[ns]',
#                 'exit_price': 'float64',
#                 'gross_pnl': 'float64',
#                 'net_pnl': 'float64',
#                 'exit_reason': 'string'  # String dtype for exit_reason
#             }, errors='ignore')
            
#             if os.path.exists(TradeManager.TRADE_FILE):
#                 existing = pd.read_csv(TradeManager.TRADE_FILE)
#                 # Ensure existing has same dtypes
#                 for col in df.columns:
#                     if col in existing.columns:
#                         existing[col] = existing[col].astype(df[col].dtype, errors='ignore')
#                 df = pd.concat([existing, df], ignore_index=True)
            
#             df.to_csv(TradeManager.TRADE_FILE, index=False)
            
#             return trade
            
#         except Exception as e:
#             print(f"Error saving trade: {e}")
#             import traceback
#             traceback.print_exc()
#             return None
    
#     @staticmethod
#     def get_all_trades():
        
#         try:
#             if not os.path.exists(TradeManager.TRADE_FILE):
#                 return pd.DataFrame()
            
#             df = pd.read_csv(TradeManager.TRADE_FILE)
            
#             # Convert datetime columns
#             for col in ["entry_time", "signal_time", "exit_time"]:
#                 if col in df.columns:
#                     df[col] = pd.to_datetime(df[col], errors='coerce')
            
#             # Ensure exit_reason is string
#             if 'exit_reason' in df.columns:
#                 df['exit_reason'] = df['exit_reason'].fillna('').astype(str)
            
#             return df
            
#         except Exception as e:
#             print(f"Error reading trades: {e}")
#             return pd.DataFrame()
    
#     @staticmethod
#     def get_open_trades():
        
#         trades = TradeManager.get_all_trades()
        
#         if trades.empty:
#             return trades
        
#         return trades[trades["trade_status"] == "OPEN"]
    
#     @staticmethod
#     def update_stop_loss(trade_id, new_sl):
        
#         try:
#             trades = TradeManager.get_all_trades()
            
#             if trades.empty:
#                 return
            
#             trades.loc[trades["trade_id"] == trade_id, "stop_loss"] = float(new_sl)
            
#             trades.to_csv(TradeManager.TRADE_FILE, index=False)
            
#         except Exception as e:
#             print(f"Error updating stop loss: {e}")
#             import traceback
#             traceback.print_exc()
    
#     @staticmethod
#     def close_trade(trade_id, exit_time, exit_price, gross_pnl, net_pnl, exit_reason):
        
#         try:
#             trades = TradeManager.get_all_trades()
            
#             if trades.empty:
#                 return
            
#             # Ensure all values are properly typed
#             trades.loc[trades["trade_id"] == trade_id, "exit_time"] = pd.to_datetime(exit_time)
#             trades.loc[trades["trade_id"] == trade_id, "exit_price"] = float(exit_price)
#             trades.loc[trades["trade_id"] == trade_id, "gross_pnl"] = float(gross_pnl)
#             trades.loc[trades["trade_id"] == trade_id, "net_pnl"] = float(net_pnl)
#             trades.loc[trades["trade_id"] == trade_id, "exit_reason"] = str(exit_reason)
#             trades.loc[trades["trade_id"] == trade_id, "trade_status"] = "CLOSED"
            
#             trades.to_csv(TradeManager.TRADE_FILE, index=False)
            
#         except Exception as e:
#             print(f"Error closing trade: {e}")
#             import traceback
#             traceback.print_exc()

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
                "exit_time": None,
                "exit_price": None,
                "gross_pnl": None,
                "net_pnl": None,
                "exit_reason": ""
            }
            
            df = pd.DataFrame([trade])
            
            if os.path.exists(TradeManager.TRADE_FILE):
                existing = pd.read_csv(TradeManager.TRADE_FILE)
                df = pd.concat([existing, df], ignore_index=True)
            
            df.to_csv(TradeManager.TRADE_FILE, index=False)
            
            return trade
            
        except Exception as e:
            print(f"Error saving trade: {e}")
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
    
    @staticmethod
    def close_trade(trade_id, exit_time, exit_price, gross_pnl, net_pnl, exit_reason):
        
        try:
            trades = TradeManager.get_all_trades()
            
            if trades.empty:
                return
            
            trades.loc[trades["trade_id"] == trade_id, "exit_time"] = pd.to_datetime(exit_time)
            trades.loc[trades["trade_id"] == trade_id, "exit_price"] = float(exit_price)
            trades.loc[trades["trade_id"] == trade_id, "gross_pnl"] = float(gross_pnl)
            trades.loc[trades["trade_id"] == trade_id, "net_pnl"] = float(net_pnl)
            trades.loc[trades["trade_id"] == trade_id, "exit_reason"] = str(exit_reason)
            trades.loc[trades["trade_id"] == trade_id, "trade_status"] = "CLOSED"
            
            trades.to_csv(TradeManager.TRADE_FILE, index=False)
            
        except Exception as e:
            print(f"Error closing trade: {e}")