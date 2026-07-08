from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.core.security import get_current_user

# Importación de Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.faq import router as faq_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.admin import router as admin_router

app = FastAPI(
    title="Chatbot Comercial API",
    description="API para panel de administración y chatbot de WhatsApp, protegida con Google OAuth2 y JWT.",
    version="0.1.0",
)

# Configuración de CORS
# Permite que la app de Next.js (puerto 3000) pueda consumir la API de FastAPI (puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambiar a URL de producción en el futuro
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los verbos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras (incluyendo Authorization y Content-Type)
)

# Rutas Públicas (Auth y Webhooks)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])

# Rutas Protegidas (Requieren JWT Firmado real)
app.include_router(
    catalog_router, 
    prefix="/api/v1/catalog", 
    tags=["Catalog"], 
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    faq_router, 
    prefix="/api/v1/faq", 
    tags=["FAQ"], 
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    calendar_router, 
    prefix="/api/v1/calendar", 
    tags=["Calendar"], 
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    admin_router, 
    prefix="/api/v1/admin", 
    tags=["Admin"], 
    dependencies=[Depends(get_current_user)]
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "chatbot-backend", "version": "0.1.0"}