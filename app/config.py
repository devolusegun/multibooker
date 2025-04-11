import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-super-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def get_token_expiry():
    return timedelta(minutes=JWT_EXPIRE_MINUTES)
