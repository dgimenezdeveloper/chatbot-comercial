"""Endpoint de trazabilidad de recordatorios.

GET /api/v1/admin/reminder-log?business_id=1&date=2026-07-11
"""

from fastapi import APIRouter, Query

from app.db.database import SessionLocal
from app.db.models.reminder_log import ReminderLog

router = APIRouter()


@router.get("/")
async def get_reminder_log(
    business_id: int = Query(1, ge=1, description="ID del negocio"),
    date: str | None = Query(None, description="Fecha (YYYY-MM-DD)"),
):
    """Retorna el log de intentos de recordatorio."""
    db = SessionLocal()
    try:
        query = db.query(ReminderLog).filter(ReminderLog.business_id == business_id)
        if date:
            query = query.filter(ReminderLog.sent_at >= f"{date}T00:00:00")
            query = query.filter(ReminderLog.sent_at <= f"{date}T23:59:59")

        logs = query.order_by(ReminderLog.sent_at.desc()).limit(200).all()
        return {
            "business_id": business_id,
            "date": date or "all",
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "appointment_id": log.appointment_id,
                    "status": log.status,
                    "channel": log.channel,
                    "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                    "error_reason": log.error_reason,
                }
                for log in logs
            ],
        }
    finally:
        db.close()
