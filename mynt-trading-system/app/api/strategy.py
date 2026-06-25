# from fastapi import APIRouter
# import pandas as pd
# import os
# from app.backtest.exit_engine import ExitEngine  # Fixed import path
# from app.strategy.breakout_10candle import Breakout10Candle
# from app.execution.trade_manager import TradeManager

# router = APIRouter()

# @router.post("/run")
# def run_strategy():
    
#     csv_file = "data/raw/NIFTY_1m.csv"
    
#     if not os.path.exists(csv_file):
#         return {
#             "success": False,
#             "message": "Historical CSV not found"
#         }
    
#     # Remove old trades
#     trade_file = "data/trades/trades.csv"
#     if os.path.exists(trade_file):
#         os.remove(trade_file)
    
#     # Load candles
#     df = pd.read_csv(csv_file)
    
#     # Generate signals
#     strategy = Breakout10Candle()
#     signals = strategy.generate_signals(df)
    
#     print(f"Generated {len(signals)} signals")
    
#     # Save signals as trades
#     trades_created = []
#     for signal in signals:
#         trade = TradeManager.save_trade(signal)
#         trades_created.append(trade)
    
#     print(f"Created {len(trades_created)} trades")
    
#     # Process exits
#     ExitEngine.process_trades(df)
    
#     # Get updated trades
#     updated_trades = TradeManager.get_all_trades()
    
#     # Calculate summary statistics
#     if not updated_trades.empty:
#         closed_trades = updated_trades[updated_trades["trade_status"] == "CLOSED"]
        
#         if not closed_trades.empty:
#             winning_trades = closed_trades[closed_trades["net_pnl"] > 0]
#             losing_trades = closed_trades[closed_trades["net_pnl"] < 0]
            
#             summary = {
#                 "total_trades": len(updated_trades),
#                 "closed_trades": len(closed_trades),
#                 "open_trades": len(updated_trades[updated_trades["trade_status"] == "OPEN"]),
#                 "winning_trades": len(winning_trades),
#                 "losing_trades": len(losing_trades),
#                 "win_rate": (len(winning_trades) / len(closed_trades) * 100) if len(closed_trades) > 0 else 0,
#                 "net_profit": closed_trades["net_pnl"].sum() if not closed_trades.empty else 0,
#                 "avg_profit": closed_trades["net_pnl"].mean() if not closed_trades.empty else 0,
#                 "max_profit": closed_trades["net_pnl"].max() if not closed_trades.empty else 0,
#                 "max_loss": closed_trades["net_pnl"].min() if not closed_trades.empty else 0,
#             }
            
#             return {
#                 "success": True,
#                 "signals_found": len(signals),
#                 "trades_created": len(trades_created),
#                 "summary": summary,
#                 "trades": updated_trades.to_dict(orient="records")
#             }
    
#     return {
#         "success": True,
#         "signals_found": len(signals),
#         "trades_created": len(trades_created),
#         "trades": updated_trades.to_dict(orient="records") if not updated_trades.empty else []
#     }





from fastapi import APIRouter
import pandas as pd
import os
from app.backtest.exit_engine import ExitEngine
from app.strategy.breakout_10candle import Breakout10Candle
from app.execution.trade_manager import TradeManager

router = APIRouter()

@router.post("/run")
def run_strategy():
    
    try:
        csv_file = "data/raw/NIFTY_1m.csv"
        
        if not os.path.exists(csv_file):
            return {
                "success": False,
                "message": f"Historical CSV not found at {csv_file}"
            }
        
        # Remove old trades
        trade_file = "data/trades/trades.csv"
        if os.path.exists(trade_file):
            os.remove(trade_file)
            print("Removed old trades file")
        
        # Load candles
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} candles from CSV")
        
        if df.empty:
            return {
                "success": False,
                "message": "CSV file is empty"
            }
        
        # Generate signals
        strategy = Breakout10Candle()
        signals = strategy.generate_signals(df)
        
        print(f"\nGenerated {len(signals)} signals")
        
        if len(signals) == 0:
            return {
                "success": True,
                "message": "No signals generated",
                "signals_found": 0,
                "trades": []
            }
        
        # Save signals as trades
        trades_created = []
        for signal in signals:
            trade = TradeManager.save_trade(signal)
            if trade:
                trades_created.append(trade)
        
        print(f"Created {len(trades_created)} trades")
        
        # Process exits
        print("\nProcessing exits...")
        ExitEngine.process_trades(df)
        
        # Get updated trades
        updated_trades = TradeManager.get_all_trades()
        
        # Calculate summary statistics
        if not updated_trades.empty:
            closed_trades = updated_trades[updated_trades["trade_status"] == "CLOSED"]
            
            if not closed_trades.empty:
                winning_trades = closed_trades[closed_trades["net_pnl"] > 0]
                losing_trades = closed_trades[closed_trades["net_pnl"] < 0]
                
                summary = {
                    "total_trades": len(updated_trades),
                    "closed_trades": len(closed_trades),
                    "open_trades": len(updated_trades[updated_trades["trade_status"] == "OPEN"]),
                    "winning_trades": len(winning_trades),
                    "losing_trades": len(losing_trades),
                    "win_rate": round((len(winning_trades) / len(closed_trades) * 100), 2) if len(closed_trades) > 0 else 0,
                    "net_profit": round(closed_trades["net_pnl"].sum(), 2) if not closed_trades.empty else 0,
                    "avg_profit": round(closed_trades["net_pnl"].mean(), 2) if not closed_trades.empty else 0,
                    "max_profit": round(closed_trades["net_pnl"].max(), 2) if not closed_trades.empty else 0,
                    "max_loss": round(closed_trades["net_pnl"].min(), 2) if not closed_trades.empty else 0,
                }
                
                # Convert trades to serializable format
                trades_list = updated_trades.to_dict(orient="records")
                
                # Convert datetime to string for JSON serialization
                for trade in trades_list:
                    for key in ["signal_time", "entry_time", "exit_time"]:
                        if key in trade and trade[key] is not None:
                            # Check if it's a pandas Timestamp
                            if hasattr(trade[key], 'strftime'):
                                trade[key] = trade[key].strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                trade[key] = str(trade[key])
                    
                    # Handle NaN/None values
                    for key in ["exit_price", "gross_pnl", "net_pnl"]:
                        if key in trade and pd.isna(trade[key]):
                            trade[key] = None
                
                return {
                    "success": True,
                    "signals_found": len(signals),
                    "trades_created": len(trades_created),
                    "summary": summary,
                    "trades": trades_list
                }
        
        # Convert trades to serializable format
        trades_list = updated_trades.to_dict(orient="records") if not updated_trades.empty else []
        for trade in trades_list:
            for key in ["signal_time", "entry_time", "exit_time"]:
                if key in trade and trade[key] is not None:
                    if hasattr(trade[key], 'strftime'):
                        trade[key] = trade[key].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        trade[key] = str(trade[key])
            
            for key in ["exit_price", "gross_pnl", "net_pnl"]:
                if key in trade and pd.isna(trade[key]):
                    trade[key] = None
        
        return {
            "success": True,
            "signals_found": len(signals),
            "trades_created": len(trades_created),
            "trades": trades_list
        }
        
    except Exception as e:
        print(f"Error in run_strategy: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "error": traceback.format_exc()
        }