from fastapi import APIRouter
from app.api.v1.faq.router import router as faq_router

router = APIRouter()
router.include_router(faq_router)