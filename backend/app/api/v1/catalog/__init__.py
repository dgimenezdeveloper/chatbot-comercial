from fastapi import APIRouter
from app.api.v1.catalog.servicios import router as servicios_router
from app.api.v1.catalog.productos import router as productos_router

router = APIRouter()
router.include_router(servicios_router, prefix="/servicios")
router.include_router(productos_router, prefix="/productos")