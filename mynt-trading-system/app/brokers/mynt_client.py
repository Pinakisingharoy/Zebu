import hashlib
import json
from urllib import response
import requests

from app.core.config import (
    CLIENT_ID,
    SECRET_KEY,
    TOKEN_URL
)


class MyntClient:

    BASE_URL = "https://go.mynt.in"

    @staticmethod
    def generate_checksum(code: str):

        text = CLIENT_ID + SECRET_KEY + code

        return hashlib.sha256(
            text.encode()
        ).hexdigest()

    @staticmethod
    def generate_access_token(code: str):

        payload = {
            "code": code,
            "checksum": MyntClient.generate_checksum(code)
        }

        response = requests.post(
            TOKEN_URL,
            headers={
                "Content-Type": "text/plain"
            },
            data=f"jData={json.dumps(payload)}"
        )

        return response.json()

    # def get_historical_data(
    #     self,
    #     access_token,
    #     uid,
    #     exch,
    #     token,
    #     start_epoch,
    #     end_epoch,
    #     interval
    # ):

    #     payload = {
    #         "uid": uid,
    #         "exch": exch,
    #         "token": token,
    #         "st": str(start_epoch),
    #         "et": str(end_epoch),
    #         "intrv": str(interval)
    #     }

    #     response = requests.post(
    #         f"{self.BASE_URL}/NorenWClientAPI/TPSeries",
    #         headers={
    #             "Authorization":
    #             f"Bearer {access_token}",

    #             "Content-Type":
    #             "text/plain"
    #         },
    #         data=f"jData={json.dumps(payload)}"
    #     )

    #     return response.json()
    def get_historical_data(
        self,
        access_token,
        uid,
        exch,
        token,
        start_epoch,
        end_epoch,
        interval
):

        payload = {
            "uid": uid,
            "exch": exch,
            "token": token,
            "st": str(start_epoch),
            "et": str(end_epoch),
            "intrv": str(interval)
    }

        print("=" * 50)
        print("TPSeries Payload")
        print(payload)
        print("=" * 50)

        response = requests.post(
            f"{self.BASE_URL}/NorenWClientAPI/TPSeries",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "text/plain"
            },
            data=f"jData={json.dumps(payload)}"
    )

        print("=" * 50)
        print("TPSeries Response")
        print(response.text)
        print("=" * 50)

        return response.json()