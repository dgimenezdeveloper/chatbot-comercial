"""Endpoint de umbrales configurables por negocio.

GET /api/v1/admin/metric-thresholds?business_id=1
PUT /api/v1/admin/metric-thresholds
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.metric_threshold import MetricThreshold

router = APIRouter()


class ThresholdItem(BaseModel):
    """Schema de validación para un threshold individual."""

    metric_name: str = Field(..., min_length=1, description="Nombre de la métrica (ej: conversion_rate)")
    warning_value: float = Field(..., description="Valor del umbral warning")
    critical_value: float = Field(..., description="Valor del umbral critical")
    operator: Literal["lt", "gt"] = Field("lt", description="lt: menor es peor, gt: mayor es peor")

    @model_validator(mode="after")
    def validate_threshold_order(self):
        """Valida que warning y critical tengan la relación correcta según el operador."""
        if self.operator == "lt":
            # lt: menor es peor → critical debe ser menor (más grave) que warning
            if self.critical_value >= self.warning_value:
                raise ValueError(
                    f"Para operator='lt', critical_value ({self.critical_value}) "
                    f"debe ser menor que warning_value ({self.warning_value})"
                )
        elif self.operator == "gt":
            # gt: mayor es peor → critical debe ser mayor (más grave) que warning
            if self.critical_value <= self.warning_value:
                raise ValueError(
                    f"Para operator='gt', critical_value ({self.critical_value}) "
                    f"debe ser mayor que warning_value ({self.warning_value})"
                )
        return self


@router.get("/")
async def get_metric_thresholds(
    business_id: int = Query(1, ge=1, description="ID del negocio"),
    db: Session = Depends(get_db),
):
    """Retorna los thresholds del negocio. Si no tiene, retorna los defaults del sistema."""
    biz_thresholds = (
        db.query(MetricThreshold)
        .filter(MetricThreshold.business_id == business_id)
        .all()
    )
    if biz_thresholds:
        return {
            "business_id": business_id,
            "source": "business",
            "thresholds": [
                {
                    "metric_name": t.metric_name,
                    "warning_value": t.warning_value,
                    "critical_value": t.critical_value,
                    "operator": t.operator,
                }
                for t in biz_thresholds
            ],
        }

    default_thresholds = (
        db.query(MetricThreshold)
        .filter(MetricThreshold.business_id.is_(None))
        .all()
    )
    return {
        "business_id": business_id,
        "source": "system_default",
        "thresholds": [
            {
                "metric_name": t.metric_name,
                "warning_value": t.warning_value,
                "critical_value": t.critical_value,
                "operator": t.operator,
            }
            for t in default_thresholds
        ],
    }


@router.put("/")
async def update_metric_thresholds(
    business_id: int = Body(..., ge=1, description="ID del negocio"),
    thresholds: list[ThresholdItem] = Body(..., description="Lista de thresholds a configurar"),
    db: Session = Depends(get_db),
):
    """Upsert de thresholds para un negocio. Cada item debe tener:
    metric_name, warning_value, critical_value, operator (lt/gt).

    Usa INSERT ... ON CONFLICT para evitar race conditions en escrituras concurrentes.
    """
    updated = []
    for item in thresholds:
        stmt = pg_insert(MetricThreshold).values(
            business_id=business_id,
            metric_name=item.metric_name,
            warning_value=item.warning_value,
            critical_value=item.critical_value,
            operator=item.operator,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_business_metric_threshold",
            set_={
                "warning_value": item.warning_value,
                "critical_value": item.critical_value,
                "operator": item.operator,
            },
        )
        db.execute(stmt)
        updated.append(item.metric_name)

    db.commit()
    return {
        "business_id": business_id,
        "updated_count": len(updated),
        "updated_metrics": updated,
        "thresholds": [
            {
                "metric_name": item.metric_name,
                "warning_value": item.warning_value,
                "critical_value": item.critical_value,
                "operator": item.operator,
            }
            for item in thresholds
        ],
    }
