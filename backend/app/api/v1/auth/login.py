from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
import httpx
from app.core.settings import settings
from app.core.security import create_access_token

router = APIRouter()

@router.get("/login", summary="Redirige al login de Google")
async def login_google():
    """
    Genera la URL de autorización de Google y redirige al usuario.
    """
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline"
    )
    return RedirectResponse(url=google_auth_url)

@router.get("/callback", summary="Callback de Google OAuth2")
async def auth_callback(code: str):
    """
    Recibe el código de Google, lo intercambia por un token, obtiene el email del usuario
    y devuelve nuestro propio JWT para que el frontend lo use en la API.
    """
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Intercambiar código por token de Google
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al autenticar con Google")
        
        token_data = response.json()
        google_access_token = token_data.get("access_token")
        
        # 2. Obtener información del usuario (Email)
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {google_access_token}"}
        user_response = await client.get(user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al obtener datos del usuario")
        
        user_info = user_response.json()
        email = user_info.get("email")
        
        # 3. Generar nuestro propio JWT
        jwt_token = create_access_token(data={"sub": email, "role": "admin"})
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "email": email,
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }
        }