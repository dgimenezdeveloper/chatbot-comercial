from fastapi import APIRouter
from app.api.v1.admin.negocio import router as negocio_router
from app.api.v1.admin.metrics import router as metrics_router

router = APIRouter()
router.include_router(negocio_router, prefix="/negocio")
router.include_router(metrics_router, prefix="/metrics")