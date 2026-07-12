from fastapi import APIRouter, status
from typing import List
from app.schemas.catalog import ServicioRequest, ServicioResponse

router = APIRouter()

@router.get("/", response_model=List[ServicioResponse], status_code=status.HTTP_200_OK)
async def listar_servicios():
    return [
        ServicioResponse(id=1, nombre="Corte Clásico", descripcion="Corte de cabello tradicional", duracion_minutos=30, precio=1500.0),
        ServicioResponse(id=2, nombre="Perfilado de Barba", descripcion="Arreglo y perfilado", duracion_minutos=20, precio=800.0)
    ]

@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def crear_servicio(payload: ServicioRequest):
    return ServicioResponse(id=3, **payload.model_dump())

@router.put("/{servicio_id}", response_model=ServicioResponse, status_code=status.HTTP_200_OK)
async def actualizar_servicio(servicio_id: int, payload: ServicioRequest):
    return ServicioResponse(id=servicio_id, **payload.model_dump())

@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_servicio(servicio_id: int):
    return None