from fastapi import APIRouter, status
from typing import List
from app.schemas.calendar import TurnoRequest, TurnoResponse

router = APIRouter()

@router.get("/", response_model=List[TurnoResponse], status_code=status.HTTP_200_OK)
async def listar_turnos():
    return [
        TurnoResponse(id=1, telefono="5491123456789", servicio_id=1, fecha="2026-07-03", hora="10:00", estado="confirmado"),
        TurnoResponse(id=2, telefono="5491198765432", servicio_id=2, fecha="2026-07-03", hora="11:30", estado="pendiente")
    ]

@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
async def crear_turno(payload: TurnoRequest):
    return TurnoResponse(id=3, estado="confirmado", **payload.model_dump())

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_turno(turno_id: int):
    return None