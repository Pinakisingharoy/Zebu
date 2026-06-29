

# from fastapi import APIRouter, Depends, HTTPException
# from datetime import datetime
# import pandas as pd
# import os
# from app.api.auth import verify_token
# from app.execution.trade_manager import TradeManager

# router = APIRouter()

# @router.get("/dashboard-data")
# async def get_dashboard_data(username: str = Depends(verify_token)):
#     """Get dashboard data"""
    
#     # Get trade statistics
#     trades = TradeManager.get_all_trades()
    
#     total_trades = len(trades)
#     open_trades = len(trades[trades["trade_status"] == "OPEN"]) if not trades.empty else 0
#     closed_trades = len(trades[trades["trade_status"] == "CLOSED"]) if not trades.empty else 0
    
#     net_pnl = 0
#     winning_trades = 0
#     losing_trades = 0
    
#     if not trades.empty and closed_trades > 0:
#         closed_df = trades[trades["trade_status"] == "CLOSED"]
#         net_pnl = closed_df["net_pnl"].sum() if "net_pnl" in closed_df.columns else 0
#         winning_trades = len(closed_df[closed_df["net_pnl"] > 0]) if "net_pnl" in closed_df.columns else 0
#         losing_trades = len(closed_df[closed_df["net_pnl"] < 0]) if "net_pnl" in closed_df.columns else 0
    
#     # Check market status
#     now = datetime.now()
#     is_weekday = now.weekday() < 5
#     market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
#     market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
#     is_market_hours = market_open_time <= now <= market_close_time
#     market_status = "Open" if (is_weekday and is_market_hours) else "Closed"
    
#     return {
#         "user": {
#             "username": username,
#             "status": "Active"
#         },
#         "account": {
#             "balance": 1000000.00,
#             "status": "Active"
#         },
#         "statistics": {
#             "total_trades": total_trades,
#             "open_trades": open_trades,
#             "closed_trades": closed_trades,
#             "net_pnl": float(net_pnl),
#             "winning_trades": winning_trades,
#             "losing_trades": losing_trades,
#             "win_rate": round((winning_trades / closed_trades * 100), 2) if closed_trades > 0 else 0
#         },
#         "market": {
#             "status": market_status,
#             "current_time": now.strftime("%Y-%m-%d %H:%M:%S")
#         }
#     }

# @router.get("/trades")
# async def get_trades(username: str = Depends(verify_token)):
#     """Get all trades"""
#     trades = TradeManager.get_all_trades()
    
#     if trades.empty:
#         return {"trades": []}
    
#     # Convert to serializable format
#     trades_list = trades.to_dict(orient="records")
    
#     # Convert datetime to string
#     for trade in trades_list:
#         for key in ["signal_time", "entry_time", "exit_time"]:
#             if key in trade and trade[key] is not None:
#                 if hasattr(trade[key], 'strftime'):
#                     trade[key] = trade[key].strftime("%Y-%m-%d %H:%M:%S")
#                 else:
#                     trade[key] = str(trade[key])
        
#         for key in ["exit_price", "gross_pnl", "net_pnl"]:
#             if key in trade and pd.isna(trade[key]):
#                 trade[key] = None
    
#     return {"trades": trades_list}

from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import datetime
import pandas as pd
import os
from app.api.auth import verify_token
from app.execution.trade_manager import TradeManager

router = APIRouter()

@router.get("/dashboard-data")
async def get_dashboard_data(authorization: str = Header(None)):
    """Get dashboard data"""
    try:
        # Verify token and get username
        username = verify_token(authorization)
        
        # Get trade statistics
        trades = TradeManager.get_all_trades()
        
        total_trades = len(trades)
        open_trades = len(trades[trades["trade_status"] == "OPEN"]) if not trades.empty else 0
        closed_trades = len(trades[trades["trade_status"] == "CLOSED"]) if not trades.empty else 0
        
        net_pnl = 0
        winning_trades = 0
        losing_trades = 0
        
        if not trades.empty and closed_trades > 0:
            closed_df = trades[trades["trade_status"] == "CLOSED"]
            net_pnl = closed_df["net_pnl"].sum() if "net_pnl" in closed_df.columns else 0
            winning_trades = len(closed_df[closed_df["net_pnl"] > 0]) if "net_pnl" in closed_df.columns else 0
            losing_trades = len(closed_df[closed_df["net_pnl"] < 0]) if "net_pnl" in closed_df.columns else 0
        
        # Check market status
        now = datetime.now()
        is_weekday = now.weekday() < 5
        market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
        is_market_hours = market_open_time <= now <= market_close_time
        market_status = "Open" if (is_weekday and is_market_hours) else "Closed"
        
        return {
            "user": {
                "username": username,
                "status": "Active"
            },
            "account": {
                "balance": 1000000.00,
                "status": "Active"
            },
            "statistics": {
                "total_trades": int(total_trades),
                "open_trades": int(open_trades),
                "closed_trades": int(closed_trades),
                "net_pnl": float(net_pnl),
                "winning_trades": int(winning_trades),
                "losing_trades": int(losing_trades),
                "win_rate": round((winning_trades / closed_trades * 100), 2) if closed_trades > 0 else 0
            },
            "market": {
                "status": market_status,
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trades(authorization: str = Header(None)):
    """Get all trades"""
    try:
        # Verify token
        username = verify_token(authorization)
        
        trades = TradeManager.get_all_trades()
        
        if trades.empty:
            return {"trades": []}
        
        # Convert to serializable format
        trades_list = trades.to_dict(orient="records")
        
        # Convert datetime to string
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
        
        return {"trades": trades_list}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Trades error: {e}")
        raise HTTPException(status_code=500, detail=str(e))