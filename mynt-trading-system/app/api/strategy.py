from fastapi import APIRouter
import pandas as pd
import os

from app.strategy.breakout_10candle import (
    Breakout10Candle
)

from app.execution.trade_manager import (
    TradeManager
)

router = APIRouter()


@router.post("/run")
def run_strategy():

    csv_file = "data/raw/NIFTY_1m.csv"

    if not os.path.exists(csv_file):

        return {
            "success": False,
            "message": "Historical CSV not found"
        }

    # Remove old trades

    trade_file = "data/trades/trades.csv"

    if os.path.exists(trade_file):
        os.remove(trade_file)

    # Load candles

    df = pd.read_csv(csv_file)

    strategy = Breakout10Candle()

    signals = strategy.generate_signals(df)

    trades = []

    for signal in signals:

        trade = (
            TradeManager.save_trade(
                signal
            )
        )

        trades.append(trade)

    return {

        "success": True,

        "signals_found":
        len(signals),

        "trades_created":
        len(trades),

        "trades":
        trades
    }