from fastapi import FastAPI
from app.core.settings import settings
from app.api.v1.chatbot.chat import router as chat_router
from app.api.v1.chatbot.webhook import router as webhook_router

app = FastAPI(
    title="Chatbot Comercial API",
    description="API para chatbot comercial — WhatsApp Business API (Meta WABA)",
    version="0.1.0",
)

# Registro de los routers del Chatbot con el prefijo v1 exigido en el issue
app.include_router(
    chat_router,
    prefix="/api/v1/chatbot",
    tags=["Chatbot"]
)

app.include_router(
    webhook_router,
    prefix="/api/v1/chatbot",
    tags=["Chatbot"]
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "chatbot-backend", "version": "0.1.0"}