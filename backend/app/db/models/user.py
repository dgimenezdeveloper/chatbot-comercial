"""Modelo de usuario — perfiles que acceden al panel de administración.

Cada usuario pertenece a un negocio (multi-tenant). Soporta autenticación por OAuth
(Google) y por contraseña interna. Los roles definen permisos granulares dentro
del dashboard.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    """Usuarios que administran un negocio desde el dashboard."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio al que pertenece el usuario",
    )

    # Información personal
    name = Column(
        String(200), nullable=False,
        comment="Nombre completo del usuario",
    )
    email = Column(
        String(255), unique=True, index=True, nullable=True,
        comment="Email para notificaciones y login",
    )
    phone = Column(
        String(20), index=True, nullable=True,
        comment="Número de WhatsApp personal",
    )

    # Rol y estado
    role = Column(
        Enum("admin", "operator", "guest", name="user_role"),
        default="guest",
        comment="admin=todo, operator=chatbot limitado, guest=read-only",
    )
    is_active = Column(
        Boolean, default=True,
        comment="Usuario activo en el sistema",
    )

    # Autenticación
    password_hash = Column(
        String(256), nullable=True,
        comment="Hash de contraseña para login (si aplica)",
    )
    oauth_provider = Column(
        String(50), nullable=True,
        comment="Proveedor OAuth usado (ej: 'google')",
    )
    oauth_id = Column(
        String(100), unique=True, nullable=True,
        comment="ID del usuario en el proveedor OAuth",
    )

    # Permisos granulares
    can_manage_appointments = Column(
        Boolean, default=False,
        comment="Puede gestionar turnos",
    )
    can_view_analytics = Column(
        Boolean, default=False,
        comment="Puede ver dashboard de métricas",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )

    __table_args__ = (
        UniqueConstraint("phone", "business_id", name="uq_user_phone_business"),
    )
