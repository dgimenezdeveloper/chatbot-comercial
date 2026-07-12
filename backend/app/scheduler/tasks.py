"""Celery tasks para el envío de recordatorios automáticos."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.db.database import SessionLocal
from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.db.models.events import Event
from app.db.models.reminder_log import ReminderLog
from app.scheduler.config import celery_app
from app.services.whatsapp import send_message
from app.services.event_logger import log_event

logger = logging.getLogger(__name__)


@celery_app.task(name="app.scheduler.tasks.send_reminders")
def send_reminders() -> dict:
    """Envía recordatorios a turnos de mañana.

    Flujo (4 niveles):
    1. Templates pagos → enviar sin restricción
    2. Ventana 24h → texto normal
    3. Canal alternativo → SMS/email
    4. Fallback → notificar al dueño
    """
    db = SessionLocal()
    try:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.scheduled_date >= tomorrow_start,
                Appointment.scheduled_date <= tomorrow_end,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.notification_sent_at.is_(None),
            )
            .all()
        )

        if not appointments:
            logger.info("send_reminders: 0 turnos para mañana")
            return {"total": 0, "sent": 0, "failed": 0, "notified_owner": 0}

        # Un solo event loop para todos los envíos asíncronos
        results = asyncio.run(_process_reminders(db, appointments))
        db.commit()
        logger.info("send_reminders: completo — %s", results)
        return results
    finally:
        db.close()


async def _process_reminders(db, appointments) -> dict:
    """Procesa todos los recordatorios en un solo event loop asyncio."""
    results = {"total": len(appointments), "sent": 0, "failed": 0, "notified_owner": 0}

    for appt in appointments:
        business = db.query(Business).filter(Business.id == appt.business_id).first()
        if not business:
            logger.warning("send_reminders: negocio no encontrado para appointment %s", appt.id)
            continue

        log_entry = ReminderLog(
            appointment_id=appt.id,
            business_id=appt.business_id,
            status="failed",
            channel="whatsapp_text",
        )

        try:
            # Nivel 1: Templates pagos
            if business.use_whatsapp_templates:
                await _send_template_reminder(appt, business)
                log_entry.status = "sent"
                log_entry.channel = "whatsapp_template"
                results["sent"] += 1

            # Nivel 2: Ventana 24h
            elif _within_24h_window(db, appt):
                await send_message(
                    phone=appt.user_phone or "",
                    text=f"Recordatorio: tenés un turno mañana a las {appt.scheduled_date.strftime('%H:%M')}.",
                )
                log_entry.status = "sent"
                log_entry.channel = "whatsapp_text"
                results["sent"] += 1

            # Nivel 3: Canal alternativo
            elif _has_alternative_channel(business):
                log_entry.status = "fallback_channel"
                log_entry.channel = "sms"
                log_entry.error_reason = "outside_24h_window"
                results["failed"] += 1
                logger.warning(
                    "send_reminders: fuera de ventana 24h, sms configurado para appt %s", appt.id
                )

            # Nivel 4: Notificar dueño
            else:
                if business.owner_phone:
                    await send_message(
                        phone=business.owner_phone,
                        text=(
                            f"No se pudo enviar recordatorio a {appt.user_name or appt.user_phone}\n"
                            f"Turno: mañana a las {appt.scheduled_date.strftime('%H:%M')}\n"
                            f"Servicio ID: {appt.service_id}"
                        ),
                    )
                log_entry.status = "notified_owner"
                log_entry.channel = "whatsapp_text"
                log_entry.error_reason = "all_channels_failed"
                results["notified_owner"] += 1

            # Evento de recordatorio enviado
            if log_entry.status == "sent":
                log_event(
                    session_id=appt.session_id or str(appt.user_phone or "unknown"),
                    business_id=appt.business_id,
                    event_type="reminder_sent",
                    payload={
                        "appointment_id": appt.id,
                        "channel": log_entry.channel,
                    },
                )
                appt.notification_sent_at = datetime.now(timezone.utc)

        except Exception as e:
            logger.exception("send_reminders: error para appointment %s", appt.id)
            db.rollback()
            log_entry.status = "failed"
            log_entry.error_reason = str(e)[:500]
            results["failed"] += 1

        db.add(log_entry)

    return results


def _within_24h_window(db, appointment) -> bool:
    """Verifica si el usuario está dentro de la ventana de 24h de WhatsApp
    usando el timestamp del último mensaje entrante del cliente."""
    last_message = (
        db.query(func.max(Event.timestamp))
        .filter(
            Event.business_id == appointment.business_id,
            Event.session_id == appointment.session_id,
            Event.channel == "whatsapp",
        )
        .scalar()
    )
    if not last_message:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    return last_message >= cutoff


def _has_alternative_channel(business) -> bool:
    """Verifica si hay canal alternativo configurado (placeholder)."""
    # TODO: SMS/email integration
    return False


async def _send_template_reminder(appointment, business) -> None:
    """Envía recordatorio usando template de WhatsApp."""
    await send_message(
        phone=appointment.user_phone or "",
        text=f"Recordatorio: {business.name} te espera mañana a las {appointment.scheduled_date.strftime('%H:%M')}.",
    )
