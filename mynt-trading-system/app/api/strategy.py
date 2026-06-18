from fastapi import APIRouter

import pandas as pd

from app.strategy.breakout_10candle import (
    Breakout10Candle
)

from app.execution.trade_manager import (
    TradeManager
)

router = APIRouter()


@router.post("/run")
def run_strategy():

    df = pd.read_csv(
        "data/raw/NIFTY_1m.csv"
    )

    df["datetime"] = pd.to_datetime(
    df["datetime"],
    format="%d-%m-%Y %H:%M:%S"
)

# MOST IMPORTANT

    df = df.sort_values(
        "datetime"
        ).reset_index(drop=True)

    strategy = (
        Breakout10Candle()
    )

    signals = (
        strategy.generate_signals(df)
    )

    trades = []

    for signal in signals:

        trade = (
            TradeManager.save_trade(
                signal
            )
        )

        trades.append(
            trade
        )

    return {

        "signals":
        len(signals),

        "trades":
        len(trades)
    }