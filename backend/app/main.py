from fastapi import FastAPI
from app.core.settings import settings

app = FastAPI(
    title="Chatbot Comercial API",
    description="API para chatbot comercial — WhatsApp Business API (Meta WABA)",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "chatbot-backend", "version": "0.1.0"}
