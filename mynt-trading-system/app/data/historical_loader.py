import os
import pandas as pd

from app.brokers.mynt_client import MyntClient


class HistoricalLoader:

    def __init__(self):

        self.client = MyntClient()

    def download_and_save(
        self,
        access_token,
        uid,
        symbol,
        token,
        interval,
        start_epoch,
        end_epoch
    ):

        data = self.client.get_historical_data(

            access_token=access_token,

            uid=uid,

            exch="NSE",

            token=token,

            start_epoch=start_epoch,

            end_epoch=end_epoch,

            interval=interval
        )

        print("=" * 50)
        print("RAW HISTORICAL RESPONSE")
        print(type(data))
        print(data)
        print("=" * 50)

        if not data:

            raise Exception(
                "No historical data received"
            )

        # API returned an error object
        if isinstance(data, dict):

            raise Exception(
                data.get(
                    "emsg",
                    f"Unexpected API response: {data}"
                )
            )

        # API returned something unexpected
        if not isinstance(data, list):

            raise Exception(
                f"Invalid response type: {type(data)}"
            )

        rows = []

        for candle in data:

            if not isinstance(candle, dict):
                continue

            rows.append({

                "symbol": symbol,

                "token": token,

                "datetime":
                candle.get("time"),

                "open":
                candle.get("into"),

                "high":
                candle.get("inth"),

                "low":
                candle.get("intl"),

                "close":
                candle.get("intc"),

                "volume":
                candle.get("intv")
            })

        if len(rows) == 0:

            raise Exception(
                "No candle data found"
            )

        df = pd.DataFrame(rows)

        os.makedirs(
            "data/raw",
            exist_ok=True
        )

        filename = (
            f"data/raw/"
            f"{symbol}_{interval}m.csv"
        )

        df.to_csv(
            filename,
            index=False
        )

        print(
            f"Saved {len(df)} rows "
            f"to {filename}"
        )

        return {
            "rows": len(df),
            "file": filename
        }