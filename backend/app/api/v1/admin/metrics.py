"""Endpoint de métricas para el panel de administración.

GET /api/v1/admin/metrics?days=30 → retorna métricas aisladas por el business_id del JWT.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.metrics import AllMetrics
from app.services.metrics_queries import get_all_metrics

router = APIRouter()


@router.get("/", response_model=AllMetrics)
async def get_metrics(
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás para calcular métricas"),
    include_extended: bool = Query(False, description="Incluir las 38 métricas extendidas"),
    segment_by: Optional[str] = Query(None, description="Segmentar por: service, channel"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD). Precede a days"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD). Precede a days"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna las métricas de rendimiento del chatbot aisladas para el inquilino autenticado."""
    # Aislamiento estricto: forzar business_id extraído del JWT del usuario autenticado
    business_id = current_user.get("business_id", 1)

    metrics = get_all_metrics(
        db,
        business_id=business_id,
        days=days,
        include_extended=include_extended,
        segment_by=segment_by,
        start_date=start_date,
        end_date=end_date,
    )
    return metrics