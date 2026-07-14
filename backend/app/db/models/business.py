"""Modelo de negocio — entidad raíz multi-tenant del sistema.

Cada registro representa un cliente del chatbot (peluquería, salón, barbería, etc.).
Todas las tablas de negocio referencian ``business.id`` como FK para aislamiento de datos.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Business(Base):
    """Cliente principal del sistema — raíz multi-tenant."""

    __tablename__ = "business"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    name = Column(
        String(200), nullable=False,
        comment="Nombre del negocio (ej: 'Salon Belén')",
    )
    slug = Column(
        String(100), unique=True, nullable=False, index=True,
        comment="Slug para URLs amigables /{slug}/dashboard",
    )
    description = Column(
        Text, nullable=True,
        comment="Descripción breve del negocio",
    )
    active = Column(
        Boolean, default=True,
        comment="Negocio activo en el sistema",
    )

    # Configuración WhatsApp
    whatsapp_phone_id = Column(
        String(50), nullable=True,
        comment="WhatsApp Business Phone ID",
    )
    whatsapp_business_account_id = Column(
        String(100), nullable=True,
        comment="WhatsApp Business Account ID",
    )
    whatsapp_verify_token = Column(
        String(100), nullable=True,
        comment="Verify token para el webhook de Meta",
    )

    # Configuración regional
    timezone = Column(
        String(50), default="America/Argentina/Buenos_Aires",
        comment="Timezone del negocio",
    )
    currency = Column(
        String(3), default="ARS",
        comment="Código de moneda para precios",
    )

    # Métodos de pago habilitados
    accept_cards = Column(
        Boolean, default=True,
        comment="Acepta tarjetas de crédito/débito",
    )
    accepts_cash = Column(
        Boolean, default=True,
        comment="Acepta efectivo",
    )

    # Configuración de recordatorios
    use_whatsapp_templates = Column(
        Boolean, default=False,
        comment="Usar templates pagos de Meta para recordatorios (sin restricción 24h)",
    )
    owner_phone = Column(
        String(50), nullable=True,
        comment="WhatsApp del dueño para notificaciones de fallo de recordatorio",
    )

    # Canales alternativos de notificación
    sms_enabled = Column(
        Boolean, default=False,
        comment="SMS habilitado como canal alternativo de recordatorio",
    )
    email_enabled = Column(
        Boolean, default=False,
        comment="Email habilitado como canal alternativo de recordatorio",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación del registro",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
