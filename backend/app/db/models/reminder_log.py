"""Modelo de registro de recordatorios — trazabilidad de intentos de envío.

Cada fila representa un intento de envío de recordatorio a un cliente,
registrando el canal usado, el estado y cualquier error.
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class ReminderLog(Base):
    """Registro de intentos de envío de recordatorios."""

    __tablename__ = "reminder_log"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno")
    appointment_id = Column(
        Integer, ForeignKey("appointment.id", ondelete="SET NULL"),
        nullable=True,
        comment="Turno asociado",
    )
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False, index=True,
        comment="Negocio",
    )

    status = Column(
        Enum("sent", "failed", "outside_window", "fallback_channel", "notified_owner",
             name="reminder_status"),
        nullable=False,
        comment="Estado del intento",
    )
    channel = Column(
        Enum("whatsapp_text", "whatsapp_template", "sms", "email",
             name="reminder_channel"),
        nullable=False,
        comment="Canal usado para el envío",
    )
    sent_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Momento del intento",
    )
    error_reason = Column(
        Text, nullable=True,
        comment="Motivo de falla (si status != sent)",
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
