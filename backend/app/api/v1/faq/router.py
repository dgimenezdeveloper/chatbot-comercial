from fastapi import APIRouter, status
from typing import List
from app.schemas.faq import FAQRequest, FAQResponse

router = APIRouter()

@router.get("/", response_model=List[FAQResponse], status_code=status.HTTP_200_OK)
async def listar_faqs():
    return [
        FAQResponse(id=1, pregunta="¿Aceptan tarjetas?", respuesta="Sí, aceptamos todas las tarjetas de crédito y débito."),
        FAQResponse(id=2, pregunta="¿Dónde están ubicados?", respuesta="Nos encontramos en Av. Principal 123, Ciudad.")
    ]

@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def crear_faq(payload: FAQRequest):
    return FAQResponse(id=3, **payload.model_dump())

@router.put("/{faq_id}", response_model=FAQResponse, status_code=status.HTTP_200_OK)
async def actualizar_faq(faq_id: int, payload: FAQRequest):
    return FAQResponse(id=faq_id, **payload.model_dump())

@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_faq(faq_id: int):
    return None