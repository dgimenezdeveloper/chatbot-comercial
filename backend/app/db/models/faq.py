"""Modelo de FAQ — preguntas frecuentes del negocio.

Cada FAQ pertenece a un negocio. Se pueden categorizar y ordenar para mostrar
en el chatbot y en el dashboard.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class FAQ(Base):
    """Preguntas frecuentes asociadas a un negocio."""

    __tablename__ = "faq"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio al que pertenece la FAQ",
    )

    question = Column(
        String(500), nullable=False,
        comment="Pregunta frecuente",
    )
    answer = Column(
        Text, nullable=False,
        comment="Respuesta a la pregunta frecuente",
    )

    order = Column(
        Integer, default=0, nullable=True,
        comment="Orden de visualización (menor primero)",
    )
    is_active = Column(
        Boolean, default=True,
        comment="FAQ activa y visible",
    )

    category = Column(
        String(100), nullable=True,
        comment="Categoría (ej: 'precios', 'turnos', 'pagos')",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
