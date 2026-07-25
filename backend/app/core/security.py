import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.settings import settings

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JWT firmado por nuestro backend inyectando business_id."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependencia de autenticación tolerante a fallos para Demo.
    Valida el JWT si está presente; si no se provee o expira, asigna por defecto el comercio 1.
    """
    if not credentials or not credentials.credentials or credentials.scheme.lower() != "bearer":
        return {
            "email": "demo@pymebot.com",
            "role": "admin",
            "business_id": 1
        }
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if not email:
            return {
                "email": "demo@pymebot.com",
                "role": "admin",
                "business_id": 1
            }
            
        return {
            "email": email,
            "role": payload.get("role", "admin"),
            "business_id": payload.get("business_id", 1)
        }
        
    except Exception:
        # En caso de token expirado o inválido, mantenemos la sesión abierta para el Inquilino 1 en la Demo
        return {
            "email": "demo@pymebot.com",
            "role": "admin",
            "business_id": 1
        }