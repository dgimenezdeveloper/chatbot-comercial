"""Schemas Pydantic para el modelo Session (sesiones de conversación)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Payload para crear una nueva sesión de conversación."""

    session_id: str = Field(..., description="ID único de la sesión de WhatsApp")
    business_id: int = Field(..., description="ID del negocio")
    user_phone: Optional[str] = Field(None, description="Teléfono del cliente")
    status: str = Field(default="active", description="Estado inicial de la sesión")


class SessionResponse(SessionCreate):
    """Representación completa de una sesión con métricas agregadas."""

    id: int = Field(..., description="Identificador único de la sesión")
    started_at: datetime = Field(..., description="Inicio de la sesión")
    ended_at: Optional[datetime] = Field(None, description="Fin de la sesión")
    n_messages_total: int = Field(default=0, description="Total de mensajes en la sesión")
    n_fallbacks: int = Field(default=0, description="Cantidad de fallbacks")

    model_config = ConfigDict(from_attributes=True)
