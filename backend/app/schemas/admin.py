from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class NegocioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre comercial del negocio")
    descripcion: str = Field(..., description="Descripción del negocio")
    categoria: Optional[str] = Field(None, description="Macro-categoría del negocio")
    direccion: Optional[str] = Field(None, description="Dirección del local")
    telefono: Optional[str] = Field(None, description="Teléfono de contacto")
    email: Optional[str] = Field(None, description="Email de contacto")
    website: Optional[str] = Field(None, description="Sitio web")
    instagram: Optional[str] = Field(None, description="Instagram")
    facebook: Optional[str] = Field(None, description="Facebook")
    tiktok: Optional[str] = Field(None, description="TikTok")
    twitter: Optional[str] = Field(None, description="X (Twitter)")
    horarios: str = Field(..., description="Horarios de atención al público")
    contacto: str = Field(..., description="Información de contacto compilada")
    owner_phone: Optional[str] = Field(None, description="WhatsApp del dueño para notificaciones")
    google_calendar_id: Optional[str] = Field(None, description="ID del calendario en Google Calendar")
    
    # Módulos dinámicos
    enable_services: Optional[bool] = Field(True, description="Activar módulo de turnos")
    enable_products: Optional[bool] = Field(True, description="Activar módulo de catálogo")
    enable_faqs: Optional[bool] = Field(True, description="Activar módulo de consultas")

    # Recordatorios alternativos
    use_whatsapp_templates: Optional[bool] = Field(False, description="Templates oficiales Meta")
    sms_enabled: Optional[bool] = Field(False, description="SMS como canal alternativo")
    email_enabled: Optional[bool] = Field(False, description="Email como canal alternativo")

class NegocioResponse(NegocioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único de la configuración del negocio")