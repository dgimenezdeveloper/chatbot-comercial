from fastapi import APIRouter
from app.api.v1.calendar.turnos import router as turnos_router

router = APIRouter()
router.include_router(turnos_router, prefix="/turnos")