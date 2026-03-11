from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services import user_service

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
    userID: str
    message: str


class CheckDuplicateRequest(BaseModel):
    userId: str


class CheckDuplicateResponse(BaseModel):
    available: bool


# -----------------------------
# Endpoints
# -----------------------------
@router.post(
    "/signup",
    summary="회원가입",
    response_model=AuthResponse,
)
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

    return AuthResponse(userID=user.nickname, message="Signup successful")


@router.post(
    "/login",
    summary="로그인",
    response_model=AuthResponse,
)
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

    return AuthResponse(userID=user.nickname, message="Login successful")


@router.post(
    "/check-duplicate",
    summary="닉네임 중복 확인",
    response_model=CheckDuplicateResponse,
)
def check_duplicate(in_: CheckDuplicateRequest, db: Session = Depends(get_db)):
    if not in_.userId or not in_.userId.strip():
        raise HTTPException(status_code=400, detail="userId is required")

    taken = user_service.is_nickname_taken(in_.userId.strip(), db)
    return CheckDuplicateResponse(available=not taken)

