from fastapi import APIRouter, status
from app.schemas.admin import NegocioRequest, NegocioResponse

router = APIRouter()

@router.get("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def obtener_negocio():
    return NegocioResponse(
        id=1,
        nombre="Peluquería Estilo",
        descripcion="La mejor peluquería de la ciudad.",
        horarios="Lunes a Sábados de 09:00 a 20:00",
        contacto="contacto@estilo.com | +54 9 11 1234-5678"
    )

@router.put("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def actualizar_negocio(payload: NegocioRequest):
    return NegocioResponse(id=1, **payload.model_dump())