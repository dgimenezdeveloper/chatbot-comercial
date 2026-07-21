"""Modelo de evento — registro de métricas y análisis conversacional.

Cada evento representa una acción clave en el flujo del chatbot (inicio de conversación,
selección de menú, fallback, creación de turno, etc.). Usa una columna JSONB para
almacenar el payload flexible de cada tipo de evento.

Tipos de evento soportados:
- conversation_started
- menu_option_selected
- service_selected
- fallback_triggered
- appointment_created
- escalation_to_human
- csat_submitted
- reminder_sent
- reminder_response
- conversation_closed
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class Event(Base):
    """Eventos instrumentados para análisis y métricas en tiempo real."""

    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    session_id = Column(
        String(100), ForeignKey("session.session_id", ondelete="SET NULL"),
        nullable=False, index=True,
        comment="ID único de la sesión de conversación (FK a session)",
    )
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="Negocio multi-tenant",
    )

    event_type = Column(
        String(100), nullable=False,
        comment="Tipo de evento instrumentado",
    )

    payload_json = Column(
        JSONB, nullable=True,
        comment="Payload JSON con campos específicos del tipo de evento",
    )

    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Momento exacto del evento",
    )

    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="Usuario registrado asociado (NULL para guest)",
    )
    channel = Column(
        Enum("whatsapp", "web", name="event_channel"),
        default="whatsapp",
        comment="Canal de origen del evento",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación del registro",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
