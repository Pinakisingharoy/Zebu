import hashlib
import json
import requests

from app.core.config import (
    CLIENT_ID,
    SECRET_KEY,
    TOKEN_URL
)


class MyntClient:

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