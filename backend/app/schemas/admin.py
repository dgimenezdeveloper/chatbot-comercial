from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class NegocioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre comercial del negocio")
    descripcion: str = Field(..., description="Descripción del negocio")
    horarios: str = Field(..., description="Horarios de atención al público")
    contacto: str = Field(..., description="Información de contacto (teléfono, email, etc.)")
    owner_phone: Optional[str] = Field(None, description="WhatsApp del dueño para notificaciones y atención humana")

class NegocioResponse(NegocioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único de la configuración del negocio")