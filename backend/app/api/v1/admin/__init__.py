from fastapi import APIRouter
from app.api.v1.admin.negocio import router as negocio_router

router = APIRouter()
router.include_router(negocio_router, prefix="/negocio")