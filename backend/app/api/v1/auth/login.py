from fastapi import APIRouter, HTTPException, status
import httpx
from app.core.settings import settings
from app.core.security import create_access_token
from app.schemas.auth import LoginMockRequest, GoogleLoginRequest, LoginResponse

router = APIRouter()

@router.post(
    "/login", 
    response_model=LoginResponse, 
    status_code=status.HTTP_200_OK,
    summary="Login de prueba (Mock JWT)",
    description="Emite un JWT firmado interno usando credenciales estáticas mockeadas para desarrollo o QA."
)
async def login_mock(payload: LoginMockRequest):
    """
    Endpoint para pruebas rápidas que permite validar que el sistema de firmas JWT funcione.
    """
    if payload.username == "admin" and payload.password == "admin123":
        jwt_token = create_access_token(data={"sub": "admin@negocio.com", "role": "admin"})
        return LoginResponse(
            access_token=jwt_token,
            user={
                "email": "admin@negocio.com",
                "name": "Administrador de Pruebas",
                "picture": ""
            }
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Credenciales de prueba inválidas (Pruebe con admin / admin123)."
    )

@router.post(
    "/google", 
    response_model=LoginResponse, 
    status_code=status.HTTP_200_OK,
    summary="Login de Google real para NextAuth.js",
    description="Recibe el access_token de Google, lo valida contra los servidores de Google y emite nuestro JWT interno de sesión."
)
async def login_google_real(payload: GoogleLoginRequest):
    """
    Endpoint que consume el servidor de NextAuth en el frontend mediante canal trasero (POST).
    Evita redirecciones que rompan el enrutamiento interno de la SPA.
    """
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {payload.access_token}"}
    
    async with httpx.AsyncClient() as client:
        user_response = await client.get(user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token de acceso de Google inválido o expirado."
            )
        
        user_info = user_response.json()
        email = user_info.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se pudo extraer el correo electrónico del usuario desde Google."
            )
        
        # Emitimos nuestro propio JWT firmado
        jwt_token = create_access_token(data={"sub": email, "role": "admin"})
        
        return LoginResponse(
            access_token=jwt_token,
            user={
                "email": email,
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }
        )