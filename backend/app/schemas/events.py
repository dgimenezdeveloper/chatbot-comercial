"""Schemas Pydantic para el modelo Event (eventos de métricas).

Define las estructuras de request/response para registrar y consultar eventos
instrumentados del chatbot.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Payload para crear un nuevo evento de métrica."""

    session_id: str = Field(..., description="ID único de la sesión de conversación")
    business_id: int = Field(..., description="ID del negocio multi-tenant")
    event_type: str = Field(..., description="Tipo de evento instrumentado")
    payload_json: Optional[dict] = Field(None, description="Payload JSON con campos del evento")
    user_id: Optional[int] = Field(None, description="ID del usuario registrado (NULL para guest)")
    channel: str = Field(default="whatsapp", description="Canal de origen: whatsapp o web")


class EventResponse(EventCreate):
    """Representación completa de un evento, incluyendo ID y timestamp."""

    id: int = Field(..., description="Identificador único del evento")
    timestamp: datetime = Field(..., description="Momento exacto del evento")

    model_config = ConfigDict(from_attributes=True)
