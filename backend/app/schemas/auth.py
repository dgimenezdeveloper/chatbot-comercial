from pydantic import BaseModel, Field

class LoginMockRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario o email para la sesión de prueba")
    password: str = Field(..., description="Contraseña para la sesión de prueba")

class GoogleLoginRequest(BaseModel):
    access_token: str = Field(..., description="El access_token devuelto por Google OAuth2 tras el inicio de sesión en el frontend.")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Token JWT de sesión interna firmado por nuestro backend.")
    token_type: str = Field(default="bearer", description="Esquema de autenticación del token.")
    user: dict = Field(..., description="Metadatos básicos del perfil del usuario.")