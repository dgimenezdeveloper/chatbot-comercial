"""Modelo de producto — artículos vendibles del negocio.

Productos de venta directa (shampoo, ceras, aceites, etc.). Incluye control de stock
con umbral de alerta para reposición.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Product(Base):
    """Productos disponibles para la venta en el negocio."""

    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio propietario del producto",
    )

    name = Column(
        String(200), nullable=False,
        comment="Nombre del producto",
    )
    slug = Column(
        String(100), unique=True, nullable=False,
        comment="Slug para URLs amigables",
    )
    description = Column(
        Text, nullable=True,
        comment="Descripción detallada del producto",
    )

    # Precios
    price = Column(
        Numeric(10, 2), nullable=False, default=0.00,
        comment="Precio de venta al público",
    )
    cost_price = Column(
        Numeric(10, 2), nullable=True,
        comment="Costo interno para cálculo de márgenes",
    )

    # Stock
    stock_quantity = Column(
        Integer, default=0, nullable=True,
        comment="Cantidad disponible en inventario",
    )
    low_stock_threshold = Column(
        Integer, default=5,
        comment="Umbral para alerta de bajo stock",
    )

    is_active = Column(
        Boolean, default=True,
        comment="Producto activo y visible en el catálogo",
    )

    image_url = Column(
        String(500), nullable=True,
        comment="URL de imagen del producto",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
