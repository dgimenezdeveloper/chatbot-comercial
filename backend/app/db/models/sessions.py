"""Modelo de sesión — tracking de conversaciones completas.

Registra cada sesión de WhatsApp con métricas agregadas: cantidad de mensajes,
fallbacks, duración y resultado final.
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class ChatSession(Base):
    """Sesiones de conversación para analytics detallados."""

    __tablename__ = "session"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio de la sesión",
    )

    session_id = Column(
        String(100), unique=True, index=True,
        comment="ID único de sesión de WhatsApp",
    )

    # Usuario asociado
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="Usuario registrado; NULL para guest",
    )
    user_phone = Column(
        String(20), nullable=True,
        comment="Teléfono del cliente",
    )

    # Temporalidad
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Inicio de la sesión",
    )
    ended_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Fin de la sesión",
    )

    # Estado
    status = Column(
        Enum("active", "completed", "abandoned", name="session_status"),
        default="active",
        comment="Estado actual de la sesión",
    )

    # Métricas de sesión
    n_messages_total = Column(
        Integer, default=0,
        comment="Cantidad total de mensajes en la sesión",
    )
    n_fallbacks = Column(
        Integer, default=0,
        comment="Cantidad de fallbacks en la sesión",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación del registro",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
