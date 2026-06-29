# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.responses import RedirectResponse, JSONResponse
# from datetime import datetime, timedelta
# import jwt
# import os
# from typing import Optional

# from app.core.config import CLIENT_ID, LOGIN_URL, SECRET_KEY, JWT_SECRET_KEY, ALGORITHM
# from app.brokers.mynt_client import MyntClient

# router = APIRouter()

# # In-memory session storage
# session_data = {}

# # Frontend URL
# FRONTEND_URL = "http://localhost:3000"

# # ========================================
# # OAUTH ENDPOINTS
# # ========================================

# @router.get("/login")
# def login():
#     """
#     Redirect to Mynt/Zebu OAuth login page
#     """
#     oauth_url = f"{LOGIN_URL}?client_id={CLIENT_ID}"
#     return RedirectResponse(oauth_url)


# @router.get("/callback")
# def callback(code: str):
#     """
#     Handle OAuth callback from Mynt/Zebu
#     Redirect to frontend with the code
#     """
#     print("=" * 50)
#     print("AUTH CODE RECEIVED:")
#     print(code)
#     print("=" * 50)

#     # Get access token from Mynt/Zebu
#     token_response = MyntClient.generate_access_token(code)

#     print("TOKEN RESPONSE:")
#     print(token_response)

#     # Check if token generation was successful
#     if token_response.get("stat") != "Ok":
#         # Redirect to frontend with error
#         return RedirectResponse(
#             f"{FRONTEND_URL}/?error={token_response.get('emsg', 'Login failed')}"
#         )

#     # Store session data
#     session_data["access_token"] = token_response.get("access_token")
#     session_data["refresh_token"] = token_response.get("refresh_token")
#     session_data["uid"] = token_response.get("uid")
#     session_data["user_name"] = token_response.get("uname", "User")
    
#     # Generate JWT token for frontend session
#     try:
#         jwt_token = jwt.encode(
#             {
#                 "sub": session_data["uid"],
#                 "exp": datetime.utcnow() + timedelta(minutes=30),
#                 "iat": datetime.utcnow()
#             },
#             JWT_SECRET_KEY,
#             algorithm=ALGORITHM
#         )
#     except Exception as e:
#         print(f"JWT encoding error: {e}")
#         jwt_token = session_data["access_token"]

#     # Redirect to frontend with the token
#     redirect_url = f"{FRONTEND_URL}/?token={jwt_token}&username={session_data['uid']}&full_name={session_data['user_name']}"
#     print(f"Redirecting to: {redirect_url}")
    
#     return RedirectResponse(redirect_url)


# # ========================================
# # SESSION MANAGEMENT ENDPOINTS
# # ========================================

# @router.get("/session")
# def get_session():
#     """
#     Get current session data
#     """
#     if not session_data:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="No active session"
#         )
#     return {
#         "uid": session_data.get("uid"),
#         "user_name": session_data.get("user_name"),
#         "has_token": bool(session_data.get("access_token"))
#     }


# @router.post("/logout")
# def logout():
#     """
#     Logout and clear session
#     """
#     session_data.clear()
#     return {
#         "success": True,
#         "message": "Logged out successfully"
#     }


# @router.get("/verify")
# def verify():
#     """
#     Verify if current session is valid
#     """
#     if "access_token" in session_data and session_data.get("uid"):
#         return {
#             "valid": True,
#             "user": {
#                 "username": session_data.get("uid"),
#                 "full_name": session_data.get("user_name"),
#                 "status": "Active"
#             }
#         }
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Not authenticated"
#     )


# @router.get("/session-status")
# def get_session_status():
#     """
#     Get session status with expiry information
#     """
#     if "access_token" not in session_data or not session_data.get("uid"):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="No active session"
#         )
    
#     expiry_time = datetime.utcnow() + timedelta(minutes=30)
    
#     return {
#         "status": "active",
#         "expires_in": 1800,
#         "logged_in_since": datetime.utcnow().isoformat(),
#         "expires_at": expiry_time.isoformat(),
#         "user": {
#             "username": session_data.get("uid"),
#             "full_name": session_data.get("user_name")
#         }
#     }


# # ========================================
# # TOKEN VALIDATION HELPER
# # ========================================

# def verify_token(token: str):
#     """
#     Verify JWT token and return user info
#     """
#     try:
#         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token"
#             )
#         return username
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token expired"
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Token validation failed: {str(e)}"
#         )

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
import jwt
import os
from typing import Optional

from app.core.config import CLIENT_ID, LOGIN_URL, SECRET_KEY, JWT_SECRET_KEY, ALGORITHM
from app.brokers.mynt_client import MyntClient

router = APIRouter()

# In-memory session storage
session_data = {}

# Frontend URL
FRONTEND_URL = "http://localhost:3000"

# ========================================
# OAUTH ENDPOINTS
# ========================================

@router.get("/login")
def login():
    """
    Redirect to Mynt/Zebu OAuth login page
    """
    oauth_url = f"{LOGIN_URL}?client_id={CLIENT_ID}"
    return RedirectResponse(oauth_url)


@router.get("/callback")
def callback(code: str):
    """
    Handle OAuth callback from Mynt/Zebu
    Redirect to frontend with the code
    """
    print("=" * 50)
    print("AUTH CODE RECEIVED:")
    print(code)
    print("=" * 50)

    # Get access token from Mynt/Zebu
    token_response = MyntClient.generate_access_token(code)

    print("TOKEN RESPONSE:")
    print(token_response)

    # Check if token generation was successful
    if token_response.get("stat") != "Ok":
        return RedirectResponse(
            f"{FRONTEND_URL}/?error={token_response.get('emsg', 'Login failed')}"
        )

    # Store session data
    session_data["access_token"] = token_response.get("access_token")
    session_data["refresh_token"] = token_response.get("refresh_token")
    session_data["uid"] = token_response.get("uid")
    session_data["user_name"] = token_response.get("uname", "User")
    
    # Generate JWT token for frontend session
    try:
        jwt_token = jwt.encode(
            {
                "sub": session_data["uid"],
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "iat": datetime.utcnow()
            },
            JWT_SECRET_KEY,
            algorithm=ALGORITHM
        )
    except Exception as e:
        print(f"JWT encoding error: {e}")
        jwt_token = session_data["access_token"]

    # Redirect to frontend with the token
    redirect_url = f"{FRONTEND_URL}/?token={jwt_token}&username={session_data['uid']}&full_name={session_data['user_name']}"
    print(f"Redirecting to: {redirect_url}")
    
    return RedirectResponse(redirect_url)


# ========================================
# TOKEN VALIDATION HELPER - FIXED
# ========================================

def verify_token(authorization: str = Header(None)):
    """
    Verify JWT token and return user info
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization header"
        )
    
    # Remove "Bearer " prefix if present
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - no username"
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


# ========================================
# SESSION MANAGEMENT ENDPOINTS
# ========================================

@router.get("/session")
def get_session():
    """
    Get current session data
    """
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session"
        )
    return {
        "uid": session_data.get("uid"),
        "user_name": session_data.get("user_name"),
        "has_token": bool(session_data.get("access_token"))
    }


@router.post("/logout")
def logout():
    """
    Logout and clear session
    """
    session_data.clear()
    return {
        "success": True,
        "message": "Logged out successfully"
    }


@router.get("/verify")
def verify(authorization: str = Header(None)):
    """
    Verify if current session is valid
    """
    try:
        username = verify_token(authorization)
        return {
            "valid": True,
            "user": {
                "username": username,
                "status": "Active"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )