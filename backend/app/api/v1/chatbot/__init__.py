from fastapi import APIRouter
from app.api.v1.chatbot.webhook import router as webhook_router

router = APIRouter()

# Incluye las rutas del webhook dentro de este módulo
router.include_router(webhook_router)