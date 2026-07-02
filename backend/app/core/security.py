from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Instanciamos HTTPBearer. auto_error=False nos permite manejar el error 401 de forma personalizada.
security = HTTPBearer(auto_error=False)

async def verify_jwt_mock(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependencia Mock para simular la validación de un token JWT.
    Utiliza HTTPBearer para habilitar el botón 'Authorize' global en Swagger UI.
    """
    # Verificamos que se hayan enviado credenciales y que el esquema sea Bearer
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token faltante o inválido (Mock)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # En un entorno real, aquí extraeríamos el token con:
    # token = credentials.credentials
    # Y luego lo decodificaríamos/validaríamos.
    
    return {"user": "admin_mock", "role": "admin"}