"""Modelo de servicio — catálogo de prestaciones agendables.

Cada servicio pertenece a un negocio. Incluye categorización, duración estimada,
precio y disponibilidad diaria.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Service(Base):
    """Servicios ofrecidos por el negocio (cortes, tintes, tratamientos, etc.)."""

    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio propietario del servicio",
    )

    name = Column(
        String(200), nullable=False,
        comment="Nombre del servicio (ej: 'Corte de Cabello')",
    )
    slug = Column(
        String(100), unique=True, nullable=False,
        comment="Slug para URLs amigables",
    )
    description = Column(
        Text, nullable=True,
        comment="Descripción detallada del servicio",
    )

    # Categorización
    category = Column(
        Enum("corte", "coloración", "tratamiento", "barba", "otros", name="service_category"),
        nullable=False,
        comment="Categoría principal del servicio",
    )
    subcategory = Column(
        String(50), nullable=True,
        comment="Subcategoría opcional",
    )

    # Precio y duración
    price = Column(
        Numeric(10, 2), nullable=False, default=0.00,
        comment="Precio en la moneda del negocio",
    )
    duration_minutes = Column(
        Integer, default=30, nullable=True,
        comment="Duración estimada en minutos",
    )

    # Disponibilidad
    slots_available_per_day = Column(
        Integer, default=8, nullable=True,
        comment="Cantidad de slots disponibles por día",
    )
    is_active = Column(
        Boolean, default=True,
        comment="Servicio activo y visible en el catálogo",
    )

    # Stock (si aplica)
    requires_stock = Column(
        Boolean, default=False,
        comment="Indica si el servicio consume stock de producto",
    )
    stock_quantity = Column(
        Integer, nullable=True,
        comment="Cantidad disponible en stock",
    )

    image_url = Column(
        String(500), nullable=True,
        comment="URL de imagen representativa del servicio",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
