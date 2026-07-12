from fastapi import APIRouter
from app.api.v1.admin.negocio import router as negocio_router
from app.api.v1.admin.metrics import router as metrics_router
from app.api.v1.admin.metric_thresholds import router as metric_thresholds_router
from app.api.v1.admin.reminder_log import router as reminder_log_router
from app.api.v1.admin.health import router as health_router
from app.api.v1.admin.business import router as business_router

router = APIRouter()
router.include_router(negocio_router, prefix="/negocio")
router.include_router(metrics_router, prefix="/metrics")
router.include_router(metric_thresholds_router, prefix="/metric-thresholds")
router.include_router(reminder_log_router, prefix="/reminder-log")
router.include_router(health_router, prefix="/health")
router.include_router(business_router, prefix="/business")