from fastapi import FastAPI, Depends
from app.core.settings import settings
from app.core.security import verify_jwt_mock

# Importación de Routers
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.faq import router as faq_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.admin import router as admin_router

app = FastAPI(
    title="Chatbot Comercial API",
    description="API para chatbot comercial — WhatsApp Business API (Meta WABA)",
    version="0.1.0",
)

# Registro del Router de Chatbot (Público / Cliente Final)
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])

# Registro de Routers Administrativos (Protegidos con JWT Mock)
app.include_router(
    catalog_router, 
    prefix="/api/v1/catalog", 
    tags=["Catalog"], 
    dependencies=[Depends(verify_jwt_mock)]
)
app.include_router(
    faq_router, 
    prefix="/api/v1/faq", 
    tags=["FAQ"], 
    dependencies=[Depends(verify_jwt_mock)]
)
app.include_router(
    calendar_router, 
    prefix="/api/v1/calendar", 
    tags=["Calendar"], 
    dependencies=[Depends(verify_jwt_mock)]
)
app.include_router(
    admin_router, 
    prefix="/api/v1/admin", 
    tags=["Admin"], 
    dependencies=[Depends(verify_jwt_mock)]
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "chatbot-backend", "version": "0.1.0"}