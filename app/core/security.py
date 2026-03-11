import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_jwt(subject:str, *, expires_delta: timedelta, refresh: bool = False) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now+expires_delta).timestamp()),
        "typ": "refresh" if refresh else "access",
    }
    key = settings.REFRESH_SECRET_KEY if refresh else settings.ACCESS_SECRET_KEY
    return jwt.encode(payload, key, algorithm=settings.ALGORITHM)


def decode_jwt(token: str, *, refresh: bool = False) -> dict:
    key = settings.REFRESH_SECRET_KEY if refresh else settings.ACCESS_SECRET_KEY
    return jwt.decode(token, key, algorithms=[settings.ALGORITHM])