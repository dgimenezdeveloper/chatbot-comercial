"""Endpoint de métricas para el panel de administración.

GET /api/v1/admin/metrics?days=30 → retorna 12 métricas base.
GET /api/v1/admin/metrics?days=30&include_extended=true → retorna 50 métricas.
"""

from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.metrics import AllMetrics
from app.services.metrics_queries import get_all_metrics

router = APIRouter()


@router.get("/", response_model=AllMetrics)
async def get_metrics(
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás para calcular métricas"),
    business_id: int = Query(1, ge=1, description="ID del negocio"),
    include_extended: bool = Query(False, description="Incluir las 38 métricas extendidas"),
    segment_by: Optional[str] = Query(None, description="Segmentar por: service, channel"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD). Precede a days"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD). Precede a days"),
):
    """Retorna las métricas de rendimiento del chatbot (12 base + 38 extendidas opcionales)."""
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
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
    finally:
        db.close()
