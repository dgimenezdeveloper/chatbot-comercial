from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.business import Business
from app.schemas.admin import NegocioRequest, NegocioResponse

router = APIRouter()


@router.get("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def obtener_negocio(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    biz = db.query(Business).filter(Business.id == business_id).first()
    
    if biz:
        return NegocioResponse(
            id=biz.id,
            nombre=biz.name,
            descripcion=biz.description or "Sin descripción",
            horarios="Lunes a Sábados de 09:00 a 20:00",
            contacto=f"Tel: {biz.owner_phone or 'Sin teléfono'}"
        )
    
    return NegocioResponse(
        id=business_id,
        nombre=f"Comercio ID {business_id}",
        descripcion="Comercio registrado",
        horarios="Sin definir",
        contacto="Sin definir"
    )


@router.put("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def actualizar_negocio(
    payload: NegocioRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    biz = db.query(Business).filter(Business.id == business_id).first()
    if biz:
        biz.name = payload.nombre
        biz.description = payload.descripcion
        db.commit()
        db.refresh(biz)
        return NegocioResponse(id=biz.id, **payload.model_dump())
        
    return NegocioResponse(id=business_id, **payload.model_dump())