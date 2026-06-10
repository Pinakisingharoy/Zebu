from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

LOGIN_URL = os.getenv("LOGIN_URL")
TOKEN_URL = os.getenv("TOKEN_URL")

REDIRECT_URI = os.getenv("REDIRECT_URI")