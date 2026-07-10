"""Endpoint de métricas para el panel de administración.

GET /api/v1/admin/metrics?days=30 → retorna todas las 12 métricas agregadas.
"""

from fastapi import APIRouter, Query

from app.schemas.metrics import AllMetrics
from app.services.metrics_queries import get_all_metrics

router = APIRouter()


@router.get("/", response_model=AllMetrics)
async def get_metrics(
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás para calcular métricas"),
    business_id: int = Query(1, ge=1, description="ID del negocio"),
):
    """Retorna las 12 métricas de rendimiento del chatbot."""
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        metrics = get_all_metrics(db, business_id=business_id, days=days)
        return metrics
    finally:
        db.close()
