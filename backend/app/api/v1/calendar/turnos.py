from typing import List
import zoneinfo
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.appointment import Appointment
from app.db.models.service import Service
from app.schemas.calendar import TurnoRequest, TurnoResponse
from app.services.negocio import get_business_timezone, get_or_create_user
from app.services.calendar import create_appointment

router = APIRouter()


@router.get("/", response_model=List[TurnoResponse], status_code=status.HTTP_200_OK)
async def listar_turnos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna los turnos reales de PostgreSQL uniendo el nombre descriptivo del servicio y del cliente."""
    business_id = current_user.get("business_id", 1)
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)
    
    results = (
        db.query(Appointment, Service.name.label("service_name"), Service.duration_minutes.label("duration"))
        .outerjoin(Service, Appointment.service_id == Service.id)
        .filter(Appointment.business_id == business_id)
        .order_by(Appointment.scheduled_date.asc())
        .limit(200)
        .all()
    )
    
    turnos = []
    for appt, service_name, duration in results:
        # Priorizar el nombre de la DB o armar uno legible
        if appt.user_name and appt.user_name.strip():
            cliente_nombre = appt.user_name
        elif appt.user_phone:
            cliente_nombre = f"Cliente {appt.user_phone[-4:]}"
        else:
            cliente_nombre = "Cliente"

        servicio_desc = service_name or f"Servicio #{appt.service_id}"
        
        # Conversión adecuada de zona horaria a la del negocio
        fecha_str = ""
        hora_str = ""
        if appt.scheduled_date:
            dt = appt.scheduled_date
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            local_dt = dt.astimezone(tz)
            fecha_str = local_dt.strftime("%Y-%m-%d")
            hora_str = local_dt.strftime("%H:%M")

        turnos.append(
            TurnoResponse(
                id=appt.id,
                telefono=appt.user_phone or "",
                servicio_id=appt.service_id,
                fecha=fecha_str,
                hora=hora_str,
                estado=appt.status or "confirmado",
                nombre_cliente=cliente_nombre,
                nombre_servicio=servicio_desc,
                duracion_minutos=duration or 30
            )
        )
        
    return turnos


@router.post("/", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
async def crear_turno_manual(
    payload: TurnoRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un turno manualmente desde el panel de administración."""
    business_id = current_user.get("business_id", 1)
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)

    # Validar y parsear fecha/hora
    try:
        start_time = datetime.strptime(f"{payload.fecha} {payload.hora}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha u hora inválido.")

    # Validar servicio
    service = db.query(Service).filter(Service.id == payload.servicio_id, Service.business_id == business_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")

    # Obtener o crear usuario
    user = get_or_create_user(db, payload.telefono, business_id, name=payload.nombre_cliente or "")

    # Preparar datos del turno
    appt_data = {
        "business_id": business_id,
        "user_id": user.id if user else None,
        "user_phone": payload.telefono,
        "user_name": payload.nombre_cliente or user.name or f"Cliente {payload.telefono[-4:]}",
        "service_id": payload.servicio_id,
        "scheduled_date": start_time,
        "status": "confirmed",
        "created_via": "web", # Indica que fue creado desde el dashboard
        "session_id": None
    }

    try:
        appointment = create_appointment(db, appt_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el turno: {str(e)}")

    return TurnoResponse(
        id=appointment.id,
        nombre_cliente=appointment.user_name,
        telefono=appointment.user_phone or "",
        servicio_id=appointment.service_id,
        fecha=payload.fecha,
        hora=payload.hora,
        estado=appointment.status,
        nombre_servicio=service.name,
        duracion_minutos=service.duration_minutes or 30
    )