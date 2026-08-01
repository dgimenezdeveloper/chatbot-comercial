"""Router de preguntas frecuentes (FAQ) — conectado a PostgreSQL por tenant."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.faq import FAQRequest, FAQResponse
from app.services.faq import create_faq, delete_faq, get_faqs, update_faq

router = APIRouter()


@router.get("/", response_model=List[FAQResponse], status_code=status.HTTP_200_OK)
async def listar_faqs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista las preguntas frecuentes activas del negocio autenticado."""
    business_id = current_user.get("business_id", 1)
    faqs_db = get_faqs(db, business_id=business_id)
    return [
        FAQResponse(id=f.id, pregunta=f.question, respuesta=f.answer)
        for f in faqs_db
    ]


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def crear_faq_endpoint(
    payload: FAQRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva FAQ para el negocio autenticado."""
    business_id = current_user.get("business_id", 1)
    data = {
        "business_id": business_id,
        "question": payload.pregunta,
        "answer": payload.respuesta,
        "is_active": True,
    }
    new_faq = create_faq(db, data)
    return FAQResponse(id=new_faq.id, pregunta=new_faq.question, respuesta=new_faq.answer)


@router.put("/{faq_id}", response_model=FAQResponse, status_code=status.HTTP_200_OK)
async def actualizar_faq_endpoint(
    faq_id: int,
    payload: FAQRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza una FAQ existente."""
    data = {
        "question": payload.pregunta,
        "answer": payload.respuesta,
    }
    updated = update_faq(db, faq_id=faq_id, data=data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ no encontrada."
        )
    return FAQResponse(id=updated.id, pregunta=updated.question, respuesta=updated.answer)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_faq_endpoint(
    faq_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una FAQ."""
    success = delete_faq(db, faq_id=faq_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ no encontrada."
        )
    return None