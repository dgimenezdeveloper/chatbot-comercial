"""Modelo de orden de producto — reservas realizadas por los clientes."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class ProductOrder(Base):
    """Reservas de productos realizadas a través del chatbot."""

    __tablename__ = "product_order"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio al que pertenece el pedido",
    )

    user_name = Column(String(200), nullable=True, comment="Nombre del cliente")
    user_phone = Column(String(20), nullable=True, comment="Teléfono del cliente")

    items_json = Column(JSONB, nullable=False, comment="Lista de productos reservados (snapshot)")
    total_price = Column(Numeric(10, 2), nullable=False, default=0.00, comment="Precio total de la reserva")

    status = Column(
        String(50),
        default="pendiente",
        comment="Estado actual del pedido: pendiente, entregado, cancelado",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación de la reserva",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )