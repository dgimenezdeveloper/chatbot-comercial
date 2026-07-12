"""Endpoint de umbrales configurables por negocio.

GET /api/v1/admin/metric-thresholds?business_id=1
PUT /api/v1/admin/metric-thresholds
"""

from typing import Literal

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field

from app.db.database import SessionLocal
from app.db.models.metric_threshold import MetricThreshold

router = APIRouter()


class ThresholdItem(BaseModel):
    """Schema de validación para un threshold individual."""

    metric_name: str = Field(..., min_length=1, description="Nombre de la métrica (ej: conversion_rate)")
    warning_value: float = Field(..., description="Valor del umbral warning")
    critical_value: float = Field(..., description="Valor del umbral critical")
    operator: Literal["lt", "gt"] = Field("lt", description="lt: menor es peor, gt: mayor es peor")


@router.get("/")
async def get_metric_thresholds(
    business_id: int = Query(1, ge=1, description="ID del negocio"),
):
    """Retorna los thresholds del negocio. Si no tiene, retorna los defaults del sistema."""
    db = SessionLocal()
    try:
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
    finally:
        db.close()


@router.put("/")
async def update_metric_thresholds(
    business_id: int = Body(..., ge=1, description="ID del negocio"),
    thresholds: list[ThresholdItem] = Body(..., description="Lista de thresholds a configurar"),
):
    """Upsert de thresholds para un negocio. Cada item debe tener:
    metric_name, warning_value, critical_value, operator (lt/gt)."""
    db = SessionLocal()
    try:
        updated = []
        for item in thresholds:
            existing = (
                db.query(MetricThreshold)
                .filter(
                    MetricThreshold.business_id == business_id,
                    MetricThreshold.metric_name == item.metric_name,
                )
                .first()
            )
            if existing:
                existing.warning_value = item.warning_value
                existing.critical_value = item.critical_value
                existing.operator = item.operator
                updated.append(existing)
            else:
                new_t = MetricThreshold(
                    business_id=business_id,
                    metric_name=item.metric_name,
                    warning_value=item.warning_value,
                    critical_value=item.critical_value,
                    operator=item.operator,
                )
                db.add(new_t)
                updated.append(new_t)
        db.commit()
        return {
            "business_id": business_id,
            "updated_count": len(updated),
            "thresholds": [
                {
                    "metric_name": t.metric_name,
                    "warning_value": t.warning_value,
                    "critical_value": t.critical_value,
                    "operator": t.operator,
                }
                for t in updated
            ],
        }
    finally:
        db.close()
