from fastapi import FastAPI
from app.core.settings import settings
from app.api.v1.chatbot import router as chatbot_router  # Se importa el router unificado

app = FastAPI(
    title="Chatbot Comercial API",
    description="API para chatbot comercial — WhatsApp Business API (Meta WABA)",
    version="0.1.0",
)

# Registro del Router de Chatbot v1 (Agrupa chat y webhook internamente)
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "chatbot-backend", "version": "0.1.0"}