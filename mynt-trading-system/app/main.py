# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.auth import router as auth_router
# from app.api.historical import router as historical_router
# from app.api.strategy import router as strategy_router
# from app.api.dashboard import router as dashboard_router

# from fastapi.responses import RedirectResponse


# app = FastAPI(
#     title="Mynt Trading System",
#     description="Trading System with Mynt/Zebu Integration",
#     version="1.0.0"
# )


# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:5173",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:5173"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# # Include routers
# app.include_router(
#     auth_router,
#     prefix="/auth",
#     tags=["Authentication"]
# )


# app.include_router(
#     dashboard_router,
#     prefix="/api/dashboard",
#     tags=["Dashboard"]
# )



# app.include_router(
#     historical_router,
#     prefix="/historical",
#     tags=["Historical Data"]
# )


# app.include_router(
#     strategy_router,
#     prefix="/strategy",
#     tags=["Strategy"]
# )



# @app.get("/")
# def home():
#     return {
#         "status": "running",
#         "service": "MyNT Trading System",
#         "version": "1.0.0"
#     }



# # Temporary bridge route for MyNT callback
# @app.get("/callback")
# def root_callback(code: str):
#     from app.api.auth import callback
#     return callback(code)



# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import numpy as np

from app.api.auth import router as auth_router
from app.api.historical import router as historical_router
from app.api.strategy import router as strategy_router
from app.api.dashboard import router as dashboard_router

app = FastAPI(
    title="Mynt Trading System",
    description="Trading System with Mynt/Zebu Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    dashboard_router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    historical_router,
    prefix="/historical",
    tags=["Historical Data"]
)

app.include_router(
    strategy_router,
    prefix="/strategy",
    tags=["Strategy"]
)

@app.get("/")
def home():
    return {
        "status": "running",
        "service": "MyNT Trading System",
        "version": "1.0.0"
    }

# Temporary bridge route for MyNT callback
@app.get("/callback")
def root_callback(code: str):
    from app.api.auth import callback
    return callback(code)

@app.get("/health")
def health_check():
    return {"status": "healthy"}



