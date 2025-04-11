from jose import JWTError, jwt
from datetime import datetime
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, get_token_expiry

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + get_token_expiry()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
