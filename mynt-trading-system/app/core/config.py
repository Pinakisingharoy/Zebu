import os
from dotenv import load_dotenv

load_dotenv()

# Mynt/Zebu Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "your_client_id")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
LOGIN_URL = os.getenv("LOGIN_URL", "https://go.mynt.in/oauth/authorize")
TOKEN_URL = os.getenv("TOKEN_URL", "https://go.mynt.in/oauth/token")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30