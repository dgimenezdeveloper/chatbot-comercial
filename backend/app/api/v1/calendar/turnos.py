from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta, timezone
import zoneinfo

from app.db.database import get_db
from app.core.security import get_current_user
from app.db.models.appointment import Appointment
from app.db.models.service import Service
from app.db.models.business import Business

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_turnos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    business_id = current_user.get("business_id", 1)
    
    biz = db.query(Business).filter(Business.id == business_id).first()
    tz_str = biz.timezone if biz and biz.timezone else "America/Argentina/Buenos_Aires"
    tz = zoneinfo.ZoneInfo(tz_str)
    
    turnos = db.query(Appointment).filter(
        Appointment.business_id == business_id,
        Appointment.status.in_(["scheduled", "confirmed", "completed"])
    ).all()
    
    resultado = []
    for t in turnos:
        service = db.query(Service).filter(Service.id == t.service_id).first()
        svc_name = service.name if service else "Servicio General"
        duration = service.duration_minutes if service else 30
        
        # Garantizar conversión UTC a Local
        utc_dt = t.scheduled_date if t.scheduled_date.tzinfo else t.scheduled_date.replace(tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone(tz)
        end_dt = local_dt + timedelta(minutes=duration)
        
        resultado.append({
            "id": str(t.id),
            "clientName": t.user_name or t.user_phone or "Cliente",
            "serviceName": svc_name,
            "date": local_dt.strftime("%Y-%m-%d"),
            "startTime": local_dt.strftime("%H:%M"),
            "endTime": end_dt.strftime("%H:%M"),
            "status": t.status,
            "tone": "green" if t.status == "confirmed" else "yellow"
        })
        
    return resultado