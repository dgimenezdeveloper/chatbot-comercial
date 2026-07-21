"""Modelo de feedback — calificaciones de satisfacción del cliente (CSAT).

Registra el puntaje (1-5) y el resultado de la interacción para medir la calidad
del servicio del chatbot.
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class Feedback(Base):
    """Calificaciones CSAT de los clientes tras la interacción."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio de la interacción",
    )

    session_id = Column(
        String(100), nullable=False,
        comment="ID de sesión de WhatsApp asociada",
    )

    score = Column(
        Integer, nullable=False,
        comment="Puntaje de satisfacción (1 a 5)",
    )

    comment = Column(
        String(1000), nullable=True,
        comment="Comentario opcional del cliente",
    )

    outcome = Column(
        Enum("turno_exitoso", "escalado_exitoso", "abandonado", "fallback_malicioso",
             name="feedback_outcome"),
        nullable=True,
        comment="Resultado de la interacción",
    )

    submitted_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Momento de la calificación",
    )

    user_phone = Column(
        String(20), nullable=True,
        comment="Teléfono del cliente (para guest)",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación del registro",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
