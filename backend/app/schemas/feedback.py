"""Schemas Pydantic para el modelo Feedback (calificaciones CSAT)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """Payload para registrar una calificación de satisfacción."""

    business_id: int = Field(..., description="ID del negocio")
    session_id: str = Field(..., description="ID de sesión de WhatsApp")
    score: int = Field(..., ge=1, le=5, description="Puntaje de satisfacción (1 a 5)")
    comment: Optional[str] = Field(None, max_length=1000, description="Comentario opcional")
    outcome: Optional[str] = Field(
        None,
        description="Resultado: turno_exitoso, escalado_exitoso, abandonado, fallback_malicioso",
    )
    user_phone: Optional[str] = Field(None, description="Teléfono del cliente")


class FeedbackResponse(FeedbackCreate):
    """Representación completa de un feedback, incluyendo ID y timestamp."""

    id: int = Field(..., description="Identificador único del feedback")
    submitted_at: datetime = Field(..., description="Momento de la calificación")

    model_config = ConfigDict(from_attributes=True)
