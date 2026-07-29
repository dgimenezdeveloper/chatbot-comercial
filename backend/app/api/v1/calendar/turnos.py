"""Router de turnos de agenda — conectado a PostgreSQL con nombres de servicios y clientes."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.appointment import Appointment
from app.db.models.service import Service
from app.schemas.calendar import TurnoRequest, TurnoResponse

router = APIRouter()


@router.get("/", response_model=List[TurnoResponse], status_code=status.HTTP_200_OK)
async def listar_turnos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna los turnos reales de PostgreSQL uniendo el nombre descriptivo del servicio y del cliente."""
    business_id = current_user.get("business_id", 1)
    
    results = (
        db.query(Appointment, Service.name.label("service_name"))
        .outerjoin(Service, Appointment.service_id == Service.id)
        .filter(Appointment.business_id == business_id)
        .order_by(Appointment.scheduled_date.asc())
        .limit(200)
        .all()
    )
    
    turnos = []
    for appt, service_name in results:
        # Priorizar el nombre de la DB o armar uno legible
        if appt.user_name and appt.user_name.strip():
            cliente_nombre = appt.user_name
        elif appt.user_phone:
            cliente_nombre = f"Cliente {appt.user_phone[-4:]}"
        else:
            cliente_nombre = "Cliente"

        servicio_desc = service_name or f"Servicio #{appt.service_id}"
        
        turnos.append(
            TurnoResponse(
                id=appt.id,
                telefono=appt.user_phone or "",
                servicio_id=appt.service_id,
                fecha=appt.scheduled_date.strftime("%Y-%m-%d") if appt.scheduled_date else "",
                hora=appt.scheduled_date.strftime("%H:%M") if appt.scheduled_date else "",
                estado=appt.status or "confirmado",
                nombre_cliente=cliente_nombre,
                nombre_servicio=servicio_desc
            )
        )
        
    return turnos