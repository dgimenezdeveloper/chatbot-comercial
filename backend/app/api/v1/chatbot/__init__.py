from fastapi import APIRouter
from app.api.v1.chatbot.webhook import router as webhook_router
from app.api.v1.chatbot.chat import router as chat_router

router = APIRouter()

router.include_router(webhook_router)
router.include_router(chat_router)