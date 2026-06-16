from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import (
    CLIENT_ID,
    LOGIN_URL
)

from app.brokers.mynt_client import MyntClient

router = APIRouter()

session_data = {}


@router.get("/login")
def login():

    oauth_url = (
        f"{LOGIN_URL}"
        f"?client_id={CLIENT_ID}"
    )

    return RedirectResponse(oauth_url)


@router.get("/callback")
def callback(code: str):

    print("=" * 50)
    print("AUTH CODE RECEIVED:")
    print(code)
    print("=" * 50)

    token_response = (
        MyntClient.generate_access_token(code)
    )

    print("TOKEN RESPONSE:")
    print(token_response)

    if token_response.get("stat") != "Ok":

        return {
            "success": False,
            "message": token_response.get("emsg")
        }

    session_data["access_token"] = (
        token_response.get("access_token")
    )

    session_data["refresh_token"] = (
        token_response.get("refresh_token")
    )

    session_data["uid"] = (
        token_response.get("uid")
    )

    return {
        "success": True,
        "access_token":
        token_response.get(
            "access_token"
        )
    }


@router.get("/session")
def get_session():

    return session_data