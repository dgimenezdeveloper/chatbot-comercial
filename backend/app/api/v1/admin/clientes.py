"""Endpoint de gestión de clientes para el panel de administración."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.appointment import Appointment

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_clientes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    business_id = current_user.get("business_id", 1)
    
    # Consultar usuarios pertenecientes al comercio
    users = db.query(User).filter(User.business_id == business_id).all()
    
    resultado = []
    for u in users:
        # Calcular total de turnos del cliente
        appt_count = db.query(func.count(Appointment.id)).filter(
            Appointment.business_id == business_id,
            (Appointment.user_id == u.id) | (Appointment.user_phone == u.phone)
        ).scalar() or 0
        
        # Buscar fecha de última visita
        last_appt = db.query(Appointment).filter(
            Appointment.business_id == business_id,
            (Appointment.user_id == u.id) | (Appointment.user_phone == u.phone)
        ).order_by(Appointment.scheduled_date.desc()).first()
        
        last_visit = "Sin visitas"
        if last_appt:
            last_visit = last_appt.scheduled_date.strftime("%d/%m/%Y")
            
        resultado.append({
            "id": str(u.id),
            "name": u.name or f"Cliente {u.phone[-4:] if u.phone else 'N/A'}",
            "phone": u.phone or "Sin teléfono",
            "appointments": appt_count,
            "lastVisit": last_visit
        })
        
    return {
        "clients": resultado,
        "totalCount": len(resultado)
    }