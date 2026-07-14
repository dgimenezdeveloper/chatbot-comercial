"""Celery tasks para el envío de recordatorios automáticos."""

from __future__ import annotations

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
        # Use < next_day_start instead of <= end_of_day to avoid microsecond boundary issues
        next_day_start = tomorrow_start + timedelta(days=1)

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.scheduled_date >= tomorrow_start,
                Appointment.scheduled_date < next_day_start,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.notification_sent_at.is_(None),
            )
            .with_for_update(skip_locked=True)
            .limit(500)  # paginación: máximo 500 por batch para evitar OOM
            .all()
        )

        if not appointments:
            logger.info("send_reminders: 0 turnos para mañana")
            return {"total": 0, "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0}

        # Marcar notification_sent_at a nivel DB antes del envío para prevenir
        # race condition entre múltiples workers. Si el envío falla, se limpia.
        appt_ids = [a.id for a in appointments]
        db.query(Appointment).filter(
            Appointment.id.in_(appt_ids),
        ).update(
            {"notification_sent_at": datetime.now(timezone.utc)},
            synchronize_session=False,
        )
        db.flush()

        # Un solo event loop para todos los envíos asíncronos
        results = asyncio.run(_process_reminders(db, appointments))
        db.commit()
        logger.info("send_reminders: completo — %s", results)
        return results
    except Exception:
        db.rollback()
        logger.exception("send_reminders: error crítico no recuperable")
        return {"total": 0, "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0, "error": True}
    finally:
        db.close()


async def _process_reminders(db, appointments) -> dict:
    """Procesa todos los recordatorios en un solo event loop asyncio.

    Cada appointment se procesa en un savepoint independiente para que
    un fallo no descarte los ReminderLog de iteraciones previas.
    """
    results = {"total": len(appointments), "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0}

    for appt in appointments:
        business = db.query(Business).filter(Business.id == appt.business_id).first()
        if not business:
            logger.warning("send_reminders: negocio no encontrado para appointment %s", appt.id)
            continue

        # Validar que el teléfono del usuario sea válido antes de intentar cualquier envío
        phone_valid = bool(appt.user_phone and appt.user_phone.strip())
        if not phone_valid:
            log_entry = ReminderLog(
                appointment_id=appt.id,
                business_id=appt.business_id,
                status="failed",
                channel="whatsapp_text",
                error_reason="missing_phone",
            )
            db.add(log_entry)
            # Limpiar notification_sent_at — este appointment no fue notificado
            appt.notification_sent_at = None
            results["skipped"] += 1
            logger.warning("send_reminders: teléfono inválido para appt %s", appt.id)
            continue

        log_entry = ReminderLog(
            appointment_id=appt.id,
            business_id=appt.business_id,
            status="failed",
            channel="whatsapp_text",
        )

        # Savepoint: aísla cada iteración. Si falla, solo se revierte este appointment.
        try:
            with db.begin_nested():
                # Nivel 1: Templates pagos
                if business.use_whatsapp_templates:
                    await _send_template_reminder(appt, business)
                    log_entry.status = "sent"
                    log_entry.channel = "whatsapp_template"
                    results["sent"] += 1

                # Nivel 2: Ventana 24h
                elif _within_24h_window(db, appt):
                    await send_message(
                        phone=appt.user_phone,
                        text=f"Recordatorio: tenés un turno mañana a las {appt.scheduled_date.strftime('%H:%M')}.",
                    )
                    log_entry.status = "sent"
                    log_entry.channel = "whatsapp_text"
                    results["sent"] += 1

                # Nivel 3: Canal alternativo
                elif _has_alternative_channel(business):
                    log_entry.status = "outside_window"
                    log_entry.channel = "sms"
                    log_entry.error_reason = "outside_24h_window"
                    results["skipped"] += 1
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

                # Solo loggear evento y mantener notification_sent_at si se envió
                if log_entry.status == "sent":
                    log_event(
                        session_id=appt.session_id or str(appt.user_phone),
                        business_id=appt.business_id,
                        event_type="reminder_sent",
                        payload={
                            "appointment_id": appt.id,
                            "channel": log_entry.channel,
                        },
                    )
                    # notification_sent_at ya fue seteado en send_reminders() a nivel DB
                else:
                    # No se envió — limpiar notification_sent_at para reintento
                    appt.notification_sent_at = None

                db.add(log_entry)
                # El savepoint hace commit automático al salir del with

        except Exception as e:
            logger.exception("send_reminders: error para appointment %s", appt.id)
            # El savepoint ya hizo rollback automático; marcamos como failed
            log_entry.status = "failed"
            log_entry.error_reason = str(e)[:500]
            appt.notification_sent_at = None  # limpiar para reintento
            db.add(log_entry)
            results["failed"] += 1

    return results


def _within_24h_window(db, appointment) -> bool:
    """Verifica si el usuario está dentro de la ventana de 24h de WhatsApp
    usando el timestamp del último mensaje entrante del cliente.

    Si session_id es None, no hay forma de verificar la ventana → False.
    """
    if appointment.session_id is None:
        return False
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
        phone=appointment.user_phone,
        text=f"Recordatorio: {business.name} te espera mañana a las {appointment.scheduled_date.strftime('%H:%M')}.",
    )
