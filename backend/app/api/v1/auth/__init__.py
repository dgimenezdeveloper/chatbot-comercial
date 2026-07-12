from fastapi import APIRouter
from app.api.v1.auth.login import router as login_router

router = APIRouter()
router.include_router(login_router)