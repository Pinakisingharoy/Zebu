from fastapi import FastAPI

from app.api.auth import (
    router as auth_router,
    callback
)

from app.api.historical import (
    router as historical_router
)

app = FastAPI(
    title="Mynt Trading System"
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    historical_router,
    prefix="/historical",
    tags=["Historical Data"]
)


@app.get("/")
def home():

    return {
        "status": "running",
        "service": "MyNT Trading System"
    }


# Temporary bridge route
# because MyNT is redirecting to /callback

@app.get("/callback")
def root_callback(code: str):

    return callback(code)

from app.api.strategy import (
    router as strategy_router
)

app.include_router(
    strategy_router,
    prefix="/strategy",
    tags=["Strategy"]
)


