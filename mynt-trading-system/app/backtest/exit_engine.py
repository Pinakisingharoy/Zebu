
# import pandas as pd

# from app.execution.trade_manager import (
#     TradeManager
# )

# from app.strategy.trailing_sl import (
#     TrailingSL
# )


# class ExitEngine:

#     BROKERAGE = 40

#     @staticmethod
#     def process_trades(df):

#         trades = TradeManager.get_all_trades()

#         if trades.empty:
#             print("No trades found")
#             return

#         df["datetime"] = pd.to_datetime(
#             df["datetime"],
#             format="%d-%m-%Y %H:%M:%S"
#         )

#         df["low"] = pd.to_numeric(df["low"])

#         df["close"] = pd.to_numeric(df["close"])

#         for _, trade in trades.iterrows():

#             if trade["trade_status"] != "OPEN":
#                 continue

#             entry_time = pd.to_datetime(
#                 trade["entry_time"]
#             )

#             entry_price = float(
#                 trade["entry_price"]
#             )

#             current_sl = float(
#                 trade["stop_loss"]
#             )

#             quantity = int(
#                 trade["quantity"]
#             )

#             future_candles = (
#                 df[
#                     df["datetime"] > entry_time
#                 ]
#                 .copy()
#                 .reset_index(drop=True)
#             )

#             if len(future_candles) < 2:
#                 continue

#             print("\n" + "=" * 50)
#             print(
#                 f"Trade ID : {trade['trade_id']}"
#             )
#             print(
#                 f"Entry Price : {entry_price}"
#             )
#             print(
#                 f"Initial SL : {current_sl}"
#             )
#             print("=" * 50)

#             for i in range(
#                 1,
#                 len(future_candles)
#             ):

#                 previous_candle = (
#                     future_candles.iloc[i - 1]
#                 )

#                 current_candle = (
#                     future_candles.iloc[i]
#                 )

#                 previous_low = float(
#                     previous_candle["low"]
#                 )

#                 # Trailing SL
#                 new_sl = (
#                     TrailingSL.update_sl(
#                         current_sl,
#                         previous_low
#                     )
#                 )

#                 if new_sl > current_sl:

#                     current_sl = new_sl

#                     TradeManager.update_stop_loss(
#                         trade["trade_id"],
#                         current_sl
#                     )

#                     print(
#                         f"SL Updated -> {current_sl}"
#                     )

#                 current_low = float(
#                     current_candle["low"]
#                 )

#                 current_close = float(
#                     current_candle["close"]
#                 )

#                 # Exit Logic
#                 if (
#                     current_low <= current_sl
#                     or
#                     current_close <= current_sl
#                 ):

#                     exit_price = current_sl

#                     gross_pnl = (
#                         exit_price -
#                         entry_price
#                     ) * quantity

#                     net_pnl = (
#                         gross_pnl -
#                         ExitEngine.BROKERAGE
#                     )

#                     TradeManager.close_trade(
#                         trade["trade_id"],
#                         current_candle["datetime"],
#                         exit_price,
#                         gross_pnl,
#                         net_pnl,
#                         "TRAILING_SL_HIT"
#                     )

#                     print(
#                         f"Trade Closed -> "
#                         f"{trade['trade_id']}"
#                     )

#                     break

import pandas as pd
from app.execution.trade_manager import TradeManager
from app.strategy.trailing_sl import TrailingSL

class ExitEngine:
    
    BROKERAGE = 40
    MARKET_CLOSE_TIME = pd.to_datetime("15:30:00").time()
    
    @staticmethod
    def process_trades(df):
        
        try:
            trades = TradeManager.get_open_trades()
            
            if trades.empty:
                print("No open trades found")
                return
            
            # Ensure datetime format
            df["datetime"] = pd.to_datetime(
                df["datetime"],
                format="%d-%m-%Y %H:%M:%S"
            )
            
            df["low"] = pd.to_numeric(df["low"], errors='coerce')
            df["close"] = pd.to_numeric(df["close"], errors='coerce')
            df["open"] = pd.to_numeric(df["open"], errors='coerce')
            
            df = df.sort_values("datetime").reset_index(drop=True)
            
            # Group by date for proper date-wise processing
            df["trade_date"] = df["datetime"].dt.date
            
            for idx, trade in trades.iterrows():
                
                trade_id = trade["trade_id"]
                entry_time = pd.to_datetime(trade["entry_time"])
                entry_price = float(trade["entry_price"])
                current_sl = float(trade["stop_loss"])
                quantity = int(trade["quantity"])
                entry_date = entry_time.date()
                
                # Get candles after entry for the SAME DATE only
                future_candles = df[
                    (df["datetime"] > entry_time) & 
                    (df["trade_date"] == entry_date)
                ].copy().reset_index(drop=True)
                
                if len(future_candles) < 2:
                    print(f"Trade {trade_id}: No future candles on same date")
                    continue
                
                print("\n" + "=" * 60)
                print(f"Processing Trade ID: {trade_id}")
                print(f"Entry Date: {entry_date}")
                print(f"Entry Time: {entry_time}")
                print(f"Entry Price: {entry_price}")
                print(f"Initial SL: {current_sl}")
                print("=" * 60)
                
                trade_closed = False
                
                # Process candles sequentially for this trade
                for i in range(len(future_candles)):
                    
                    current_candle = future_candles.iloc[i]
                    current_time = current_candle["datetime"]
                    current_low = float(current_candle["low"])
                    current_close = float(current_candle["close"])
                    
                    # Check if market closed - exit at market close
                    if current_time.time() >= ExitEngine.MARKET_CLOSE_TIME:
                        exit_price = current_close
                        gross_pnl = (exit_price - entry_price) * quantity
                        net_pnl = gross_pnl - ExitEngine.BROKERAGE
                        
                        TradeManager.close_trade(
                            trade_id,
                            current_time,
                            exit_price,
                            gross_pnl,
                            net_pnl,
                            "MARKET_CLOSE"
                        )
                        
                        print(f"Trade {trade_id} closed at market close: {exit_price}")
                        print(f"Exit Time: {current_time}")
                        trade_closed = True
                        break
                    
                    # Update trailing SL based on previous candle LOW
                    if i > 0:
                        previous_candle = future_candles.iloc[i - 1]
                        previous_low = float(previous_candle["low"])
                        
                        # Trailing SL: Only move UP
                        new_sl = TrailingSL.update_sl(current_sl, previous_low)
                        
                        if new_sl > current_sl:
                            current_sl = new_sl
                            TradeManager.update_stop_loss(trade_id, current_sl)
                            print(f"SL Updated -> {current_sl} at {current_time}")
                    
                    # Exit Logic: Check if SL is breached
                    if current_low <= current_sl or current_close <= current_sl:
                        exit_price = current_sl
                        gross_pnl = (exit_price - entry_price) * quantity
                        net_pnl = gross_pnl - ExitEngine.BROKERAGE
                        
                        TradeManager.close_trade(
                            trade_id,
                            current_time,
                            exit_price,
                            gross_pnl,
                            net_pnl,
                            "TRAILING_SL_HIT"
                        )
                        
                        print(f"Trade {trade_id} closed at SL: {exit_price}")
                        print(f"Exit Time: {current_time}")
                        print(f"Current Low: {current_low}, Current Close: {current_close}")
                        print(f"Gross PnL: {gross_pnl:.2f}, Net PnL: {net_pnl:.2f}")
                        trade_closed = True
                        break
                
                # If trade still open after processing all candles on that date
                if not trade_closed:
                    # Close at last candle of the day
                    last_candle = future_candles.iloc[-1]
                    exit_price = float(last_candle["close"])
                    gross_pnl = (exit_price - entry_price) * quantity
                    net_pnl = gross_pnl - ExitEngine.BROKERAGE
                    
                    TradeManager.close_trade(
                        trade_id,
                        last_candle["datetime"],
                        exit_price,
                        gross_pnl,
                        net_pnl,
                        "END_OF_DAY"
                    )
                    
                    print(f"Trade {trade_id} closed at end of day: {exit_price}")
                    print(f"Exit Time: {last_candle['datetime']}")
                    
        except Exception as e:
            print(f"Error in process_trades: {e}")
            import traceback
            traceback.print_exc()
