"""Modelo de turno (appointment) — reservas de servicios agendadas.

Registra cada turno creado por el chatbot o el dashboard. Soporta clientes anónimos
(guest con teléfono) y usuarios registrados. Incluye estado del turno, canal de creación,
recordatorios y métricas de no-show.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class Appointment(Base):
    """Turnos agendados por clientes (WhatsApp o dashboard)."""

    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio del turno",
    )

    # Cliente (puede ser anónimo o registrado)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario si está registrado; NULL para guest",
    )
    user_phone = Column(
        String(20), nullable=True,
        comment="Teléfono del cliente (obligatorio para guest)",
    )
    user_name = Column(
        String(200), nullable=True,
        comment="Nombre del cliente (obligatorio para guest)",
    )

    # Servicio
    service_id = Column(
        Integer, ForeignKey("service.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Servicio reservado (no se permite borrar servicio con turnos activos)",
    )

    # Fecha y hora
    scheduled_date = Column(
        DateTime(timezone=True), nullable=False,
        comment="Fecha y hora del turno",
    )

    # Estado del turno
    status = Column(
        Enum("scheduled", "confirmed", "in_progress", "completed", "cancelled",
             name="appointment_status"),
        default="scheduled",
        comment="Estado actual del turno",
    )

    # Recordatorio y no-show
    no_show_status = Column(
        Enum("pending", "confirmed_yes", "confirmed_no", "suggested_change",
             name="no_show_status"),
        nullable=True,
        comment="Estado de confirmación del recordatorio T-24hs",
    )
    notification_sent_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Momento en que se envió la notificación/recordatorio",
    )

    # Cancelación
    cancelled_reason = Column(
        String(500), nullable=True,
        comment="Motivo de cancelación",
    )
    cancellation_scheduled_date = Column(
        DateTime(timezone=True), nullable=True,
        comment="Fecha original del turno cancelado",
    )

    # Canal de creación
    created_via = Column(
        Enum("web", "chatbot", "api", name="creation_channel"),
        default="chatbot",
        comment="Canal por el que se creó el turno: web/chatbot/api",
    )
    session_id = Column(
        String(100), nullable=True,
        comment="ID de sesión de WhatsApp asociada",
    )

    # Trazabilidad WhatsApp
    whatsapp_sent_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Timestamp de envío del mensaje de confirmación",
    )
    whatsapp_read_at = Column(
        DateTime(timezone=True), nullable=True,
        comment="Timestamp de lectura del mensaje",
    )
    whatsapp_response_type = Column(
        String(50), nullable=True,
        comment="Tipo de respuesta al recordatorio: confirmó/canceló",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
