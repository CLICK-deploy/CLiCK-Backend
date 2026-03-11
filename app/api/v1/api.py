from fastapi import APIRouter
from app.api.v1.routers import gpt, test, auth

router = APIRouter(prefix="/api")

router.include_router(auth.router, prefix="", tags=["auth"])
router.include_router(gpt.router, prefix="", tags=["improve prompt"])
router.include_router(test.router, prefix="", tags=["analyze prompt"])