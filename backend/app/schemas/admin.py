from pydantic import BaseModel, Field

class NegocioRequest(BaseModel):
    nombre: str = Field(..., description="Nombre comercial del negocio")
    descripcion: str = Field(..., description="Descripción del negocio")
    horarios: str = Field(..., description="Horarios de atención al público")
    contacto: str = Field(..., description="Información de contacto (teléfono, email, etc.)")

class NegocioResponse(NegocioRequest):
    id: int = Field(..., description="Identificador único de la configuración del negocio")