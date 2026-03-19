import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_jwt(subject: str, *, expires_delta: timedelta, refresh: bool = False) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "typ": "refresh" if refresh else "access",
    }
    key = settings.REFRESH_SECRET_KEY if refresh else settings.ACCESS_SECRET_KEY
    return jwt.encode(payload, key, algorithm=settings.ALGORITHM)


def decode_jwt(token: str, *, refresh: bool = False) -> dict:
    key = settings.REFRESH_SECRET_KEY if refresh else settings.ACCESS_SECRET_KEY
    return jwt.decode(token, key, algorithms=[settings.ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_jwt(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    nickname: str = payload.get("sub")
    if not nickname:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")
    user = db.execute(select(User).where(User.nickname == nickname)).scalar()
    if user is None:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다.")
    return user