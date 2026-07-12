"""Health check endpoint — verifica que Celery worker esté corriendo."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Verifica estado de la API y workers."""
    from app.scheduler.config import celery_app

    celery_status = "ok"
    celery_detail = None
    try:
        celery_app.control.ping(timeout=2)
    except Exception as e:
        celery_status = "degraded"
        celery_detail = str(e)

    return {
        "status": "healthy" if celery_status == "ok" else "degraded",
        "celery": celery_status,
        "celery_detail": celery_detail,
    }
