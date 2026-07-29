"""Router de configuración de negocio y gestión de clientes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.appointment import Appointment
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
            horarios=biz.horarios or "Lunes a Sábados de 09:00 a 20:00",
            contacto=biz.contacto or f"Tel: {biz.owner_phone or 'Sin teléfono'}",
            owner_phone=biz.owner_phone or ""
        )
    
    return NegocioResponse(
        id=business_id,
        nombre=f"Comercio ID {business_id}",
        descripcion="Comercio registrado",
        horarios="Sin definir",
        contacto="Sin definir",
        owner_phone=""
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
        biz.horarios = payload.horarios
        biz.contacto = payload.contacto
        if payload.owner_phone is not None:
            biz.owner_phone = payload.owner_phone
        db.commit()
        db.refresh(biz)
        return NegocioResponse(id=biz.id, **payload.model_dump())
        
    return NegocioResponse(id=business_id, **payload.model_dump())


@router.get("/clientes", status_code=status.HTTP_200_OK)
async def listar_clientes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna la lista de clientes reales (excluyendo a los administradores de la lista blanca)."""
    business_id = current_user.get("business_id", 1)

    appointments = (
        db.query(
            Appointment.user_name,
            Appointment.user_phone,
            func.count(Appointment.id).label("total_turnos"),
            func.max(Appointment.scheduled_date).label("ultimo_turno")
        )
        .filter(Appointment.business_id == business_id)
        .group_by(Appointment.user_name, Appointment.user_phone)
        .all()
    )

    client_list = []
    for idx, appt in enumerate(appointments):
        phone = appt.user_phone or "Sin teléfono"
        client_list.append({
            "id": str(idx + 1),
            "name": appt.user_name or f"Cliente {phone[-4:]}",
            "phone": phone,
            "appointments": appt.total_turnos,
            "lastVisit": appt.ultimo_turno.strftime("%d/%m/%Y") if appt.ultimo_turno else "Sin visitas"
        })

    return client_list