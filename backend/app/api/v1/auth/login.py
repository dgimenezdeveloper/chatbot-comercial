import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.security import create_access_token
from app.db.database import get_db
from app.db.models.user import User
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
    if payload.username == "admin" and payload.password == "admin123":
        jwt_token = create_access_token(data={
            "sub": "dgimenez.developer@gmail.com",
            "role": "admin",
            "business_id": 1
        })
        return LoginResponse(
            access_token=jwt_token,
            user={
                "email": "dgimenez.developer@gmail.com",
                "name": "Diego Gimenez (Peluquería)",
                "picture": "",
                "business_id": 1
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
    description="Valida el correo devuelto por Google contra la Lista Blanca estricta en la DB y emite nuestro JWT."
)
async def login_google_real(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
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
        
        # --- VALIDACIÓN ESTRICTA POR LISTA BLANCA EN DB ---
        user_db = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: El correo '{email}' no está autorizado en la lista blanca de la plataforma."
            )

        # Emitimos nuestro propio JWT firmado inyectando business_id
        jwt_token = create_access_token(data={
            "sub": email,
            "role": user_db.role,
            "business_id": user_db.business_id
        })
        
        return LoginResponse(
            access_token=jwt_token,
            user={
                "email": email,
                "name": user_db.name or user_info.get("name"),
                "picture": user_info.get("picture"),
                "business_id": user_db.business_id
            }
        )