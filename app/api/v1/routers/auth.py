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
class LoginRequest(BaseModel):
    userId: str
    password: str
    ageGroup: Optional[str] = None
    gender: Optional[str] = None


class LoginResponse(BaseModel):
    userID: str
    message: str = "Login successful"


class CheckDuplicateRequest(BaseModel):
    userId: str


class CheckDuplicateResponse(BaseModel):
    available: bool


# -----------------------------
# Endpoints
# -----------------------------
@router.post(
    "/login",
    summary="로그인 / 회원가입 (닉네임+패스워드)",
    response_model=LoginResponse,
)
def login(in_: LoginRequest, db: Session = Depends(get_db)):
    if not in_.userId or not in_.userId.strip():
        raise HTTPException(status_code=400, detail="userId is required")
    if not in_.password or not in_.password.strip():
        raise HTTPException(status_code=400, detail="password is required")

    user = user_service.register_or_login(
        nickname=in_.userId.strip(),
        password=in_.password,
        age_group=in_.ageGroup,
        gender=in_.gender,
        db=db,
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return LoginResponse(userID=user.nickname)


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
