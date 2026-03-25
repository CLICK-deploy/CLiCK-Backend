from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from jose import JWTError
from app.db.session import get_db
from app.services import user_service
from app.core.security import create_jwt, decode_jwt
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="")


# -----------------------------
# Request / Response Schemas
# -----------------------------
class SignupRequest(BaseModel):
    userId: str
    password: str
    ageGroup: Optional[str] = None
    gender: Optional[str] = None


class LoginRequest(BaseModel):
    userId: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    userID: str
    message: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str


class CheckDuplicateRequest(BaseModel):
    userId: str


class CheckDuplicateResponse(BaseModel):
    available: bool


# -----------------------------
# Endpoints
# -----------------------------
@router.post("/signup", summary="회원가입",response_model=AuthResponse,)
def signup(in_: SignupRequest, db: Session = Depends(get_db)):
    if not in_.userId or not in_.userId.strip():
        raise HTTPException(status_code=400, detail="userId is required")
    if not in_.password or not in_.password.strip():
        raise HTTPException(status_code=400, detail="password is required")

    user = user_service.signup(
        nickname=in_.userId.strip(),
        password=in_.password,
        age_group=in_.ageGroup,
        gender=in_.gender,
        db=db,
    )
    if user is None:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    access_token = create_jwt(user.nickname, expires_delta=settings.access_expires)
    refresh_token = create_jwt(user.nickname, expires_delta=settings.refresh_expires, refresh=True)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        token_type="Bearer",
        userID=user.nickname, 
        message="Signup successful"
    )


@router.post("/login", summary="로그인", response_model=AuthResponse,)
def login(in_: LoginRequest, db: Session = Depends(get_db)):
    if not in_.userId or not in_.userId.strip():
        raise HTTPException(status_code=400, detail="userId is required")

    user = user_service.login_user(
        nickname=in_.userId.strip(),
        password=in_.password,
        db=db,
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_jwt(user.nickname, expires_delta=settings.access_expires)
    refresh_token = create_jwt(user.nickname, expires_delta=settings.refresh_expires, refresh=True)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        token_type="Bearer",
        userID=user.nickname, 
        message="Login successful"
    )


@router.post("/check-duplicate", summary="닉네임 중복 확인", response_model=CheckDuplicateResponse,)
def check_duplicate(in_: CheckDuplicateRequest, db: Session = Depends(get_db)):
    if not in_.userId or not in_.userId.strip():
        raise HTTPException(status_code=400, detail="userId is required")

    taken = user_service.is_exist_user(in_.userId.strip(), db)
    return CheckDuplicateResponse(available=not taken)


@router.post("/refresh", summary="액세스 토큰 갱신", response_model=RefreshResponse)
def refresh_token(in_: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_jwt(in_.refresh_token, refresh=True)
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

    nickname: str = payload.get("sub")
    if not nickname:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")

    user = db.execute(select(User).where(User.nickname == nickname)).scalar()
    if user is None:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다.")

    user.lastLogin = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
    db.commit()

    new_access_token = create_jwt(user.nickname, expires_delta=settings.access_expires)
    return RefreshResponse(access_token=new_access_token, token_type="Bearer")

