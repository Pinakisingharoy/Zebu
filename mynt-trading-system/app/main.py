from fastapi import FastAPI

from app.api.auth import router as auth_router

app = FastAPI(
    title="Mynt Trading System"
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "MyNT Trading System"
    }