
# from fastapi import APIRouter, HTTPException, Depends
# from datetime import datetime, timedelta
# import pandas as pd
# import os
# from app.api.auth import verify_token

# router = APIRouter()

# @router.get("/download")
# async def download_historical_data(username: str = Depends(verify_token)):
#     """
#     Download historical data from Mynt/Zebu
#     """
#     try:
#         # Create data directory if it doesn't exist
#         os.makedirs("data/raw", exist_ok=True)
        
#         # Sample data generation (replace with actual Mynt API call)
#         # For demo purposes, create sample data
#         dates = pd.date_range(start="2026-06-01", end="2026-06-28", freq="1min")
#         df = pd.DataFrame({
#             "datetime": dates,
#             "symbol": "NIFTY",
#             "open": 24000 + np.random.randn(len(dates)) * 100,
#             "high": 24100 + np.random.randn(len(dates)) * 100,
#             "low": 23900 + np.random.randn(len(dates)) * 100,
#             "close": 24050 + np.random.randn(len(dates)) * 100,
#             "volume": np.random.randint(1000, 10000, len(dates))
#         })
        
#         # Save to CSV
#         csv_file = "data/raw/NIFTY_1m.csv"
#         df.to_csv(csv_file, index=False)
        
#         return {
#             "success": True,
#             "message": f"Data downloaded successfully! {len(df)} candles saved.",
#             "rows": len(df),
#             "file": csv_file
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"Download failed: {str(e)}"
#         }

from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from app.api.auth import verify_token

router = APIRouter()

@router.get("/download")
async def download_historical_data(authorization: str = Header(None)):
    """
    Download historical data from Mynt/Zebu
    """
    try:
        # Verify token
        username = verify_token(authorization)
        
        # Create data directory if it doesn't exist
        os.makedirs("data/raw", exist_ok=True)
        
        # Generate sample data
        dates = pd.date_range(start="2026-06-01", end="2026-06-28", freq="1min")
        base_price = 24000
        
        # Generate random walk prices
        np.random.seed(42)
        returns = np.random.randn(len(dates)) * 2
        prices = base_price + np.cumsum(returns)
        
        df = pd.DataFrame({
            "datetime": dates.strftime("%d-%m-%Y %H:%M:%S"),
            "symbol": "NIFTY",
            "open": prices,
            "high": prices + np.abs(np.random.randn(len(dates)) * 5),
            "low": prices - np.abs(np.random.randn(len(dates)) * 5),
            "close": prices + np.random.randn(len(dates)) * 3,
            "volume": np.random.randint(1000, 10000, len(dates))
        })
        
        # Ensure OHLC relationships are correct
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        # Round values to 2 decimal places
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].round(2)
        
        # Save to CSV
        csv_file = "data/raw/NIFTY_1m.csv"
        df.to_csv(csv_file, index=False)
        
        return {
            "success": True,
            "message": f"Data downloaded successfully! {len(df)} candles saved.",
            "rows": len(df),
            "file": csv_file
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"Download failed: {str(e)}"
        }