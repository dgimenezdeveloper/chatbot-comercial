"""Modelo de umbrales configurables por métrica y negocio.

Cada negocio puede sobrescribir los defaults del sistema (business_id=NULL)
para adaptar las alertas a sus necesidades.
"""

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class MetricThreshold(Base):
    """Umbral por métrica — business_id=NULL = default del sistema."""

    __tablename__ = "metric_thresholds"
    __table_args__ = (
        UniqueConstraint(
            "business_id", "metric_name",
            name="uq_business_metric_threshold",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, comment="ID interno")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=True,
        comment="Negocio (NULL = default del sistema)",
    )
    metric_name = Column(
        String(100), nullable=False,
        comment="Nombre de la métrica (ej: csat_average)",
    )
    warning_value = Column(
        Float, nullable=False,
        comment="Valor del umbral warning",
    )
    critical_value = Column(
        Float, nullable=False,
        comment="Valor del umbral critical",
    )
    operator = Column(
        Enum("lt", "gt", name="threshold_operator"),
        default="lt",
        comment="lt: valor menor que umbral es malo, gt: valor mayor que umbral es malo",
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
