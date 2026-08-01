from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class NegocioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre comercial del negocio")
    descripcion: str = Field(..., description="Descripción del negocio")
    categoria: Optional[str] = Field(None, description="Macro-categoría del negocio")
    horarios: str = Field(..., description="Horarios de atención al público")
    contacto: str = Field(..., description="Información de contacto (teléfono, email, etc.)")
    owner_phone: Optional[str] = Field(None, description="WhatsApp del dueño para notificaciones y atención humana")
    
    # Módulos dinámicos
    enable_services: Optional[bool] = Field(True, description="Activar módulo de turnos")
    enable_products: Optional[bool] = Field(True, description="Activar módulo de catálogo")
    enable_faqs: Optional[bool] = Field(True, description="Activar módulo de consultas")

class NegocioResponse(NegocioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único de la configuración del negocio")