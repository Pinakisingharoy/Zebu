from fastapi import APIRouter
from datetime import datetime, timedelta

from app.api.auth import session_data
from app.data.historical_loader import HistoricalLoader

router = APIRouter()


@router.post("/download")
def download_historical():

    access_token = session_data.get("access_token")
    uid = session_data.get("uid")

    if not access_token:

        return {
            "success": False,
            "message": "Login first"
        }

    # Last 5 days
    end_epoch = int(datetime.now().timestamp())

    start_epoch = int(
        (
            datetime.now()
            - timedelta(days=5)
        ).timestamp()
    )

    print("START:", start_epoch)
    print("END:", end_epoch)

    loader = HistoricalLoader()

    try:

        result = loader.download_and_save(

            access_token=access_token,

            uid=uid,

            symbol="NIFTY",

            token="26000",

            interval="1",

            start_epoch=start_epoch,

            end_epoch=end_epoch
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }