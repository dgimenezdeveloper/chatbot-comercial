"""Celery tasks para el envío de recordatorios automáticos."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.db.database import SessionLocal
from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.db.models.events import Event
from app.db.models.reminder_log import ReminderLog
from app.scheduler.config import celery_app
from app.services.metrics_types import EventType
from app.services.whatsapp import send_message
from app.services.event_logger import log_event

logger = logging.getLogger(__name__)

# Validación E.164: + seguido de 1-3 dígitos de país y 6-14 dígitos totales
_PHONE_RE = re.compile(r"^\+[1-9]\d{6,14}$")
# Formato argentino: +549 seguido de 8-10 dígitos (código de área + número)
_PHONE_AR_RE = re.compile(r"^\+549\d{8,10}$")

# Máximo de appointments por batch de recordatorio
_BATCH_SIZE = 500


def _validate_phone(phone: str | None) -> str | None:
    """Valida formato de teléfono. Retorna None si es válido, o motivo de error.

    Acepta formato E.164 internacional (+54..., +1..., etc.).
    Prefiere formato argentino (+549...) que es el caso de uso principal.
    """
    if not phone or not phone.strip():
        return "missing_phone"
    stripped = phone.strip()
    if _PHONE_AR_RE.match(stripped):
        return None  # formato argentino válido
    if _PHONE_RE.match(stripped):
        return None  # formato internacional válido
    logger.warning(
        "send_reminders: formato de teléfono no válido: %s (debe ser E.164: +[país][número])",
        stripped[:20] + "..." if len(stripped) > 20 else stripped,
    )
    return "invalid_phone_format"


@celery_app.task(name="app.scheduler.tasks.send_reminders")
def send_reminders() -> dict:
    """Envía recordatorios a turnos de mañana, procesando en batches de 500.

    Flujo (4 niveles):
    1. Templates pagos → enviar sin restricción
    2. Ventana 24h → texto normal
    3. Canal alternativo → SMS/email
    4. Fallback → notificar al dueño

    Si hay más de 500 appointments pendientes, se procesan en múltiples
    batches para asegurar que ningún turno quede sin intento de notificación.
    """
    db = SessionLocal()
    results = {"total": 0, "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0, "batches": 0}

    try:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day_start = tomorrow_start + timedelta(days=1)

        base_query = (
            db.query(Appointment)
            .filter(
                Appointment.scheduled_date >= tomorrow_start,
                Appointment.scheduled_date < next_day_start,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.notification_sent_at.is_(None),
            )
            .with_for_update(skip_locked=True)
            .order_by(Appointment.id)
        )

        # Colectar todos los appointments (con batching para limitar memoria)
        all_appointments: list[Appointment] = []
        offset = 0
        while True:
            batch = base_query.offset(offset).limit(_BATCH_SIZE).all()
            if not batch:
                break
            all_appointments.extend(batch)
            if len(batch) < _BATCH_SIZE:
                break  # último batch (incompleto)
            offset += _BATCH_SIZE

        if not all_appointments:
            logger.info("send_reminders: 0 turnos para mañana")
            return results

        results["total"] = len(all_appointments)
        results["batches"] = -(-len(all_appointments) // _BATCH_SIZE)  # ceil division

        # Procesar todos los recordatorios en un solo event loop asyncio.
        # notification_sent_at se marca individualmente en _process_reminders
        # después de cada envío exitoso (no a nivel batch).
        batch_results = asyncio.run(_process_reminders(db, all_appointments))
        results["sent"] = batch_results["sent"]
        results["failed"] = batch_results["failed"]
        results["skipped"] = batch_results["skipped"]
        results["notified_owner"] = batch_results["notified_owner"]

        db.commit()

        if results["total"] == 0:
            logger.info("send_reminders: 0 turnos para mañana")
        else:
            logger.info(
                "send_reminders: completo — %d turnos en %d batch(es): %s",
                results["total"], results["batches"],
                {k: v for k, v in results.items() if k in ("sent", "failed", "skipped", "notified_owner")},
            )
        return results
    except Exception:
        db.rollback()
        logger.exception("send_reminders: error crítico no recuperable")
        return {"total": 0, "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0, "batches": 0, "error": True}
    finally:
        db.close()


async def _process_reminders(db, appointments) -> dict:
    """Procesa todos los recordatorios en un solo event loop asyncio.

    Cada appointment se procesa en un savepoint independiente para que
    un fallo no descarte los ReminderLog de iteraciones previas.
    """
    results = {"total": len(appointments), "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0}

    # Pre-fetch all businesses in one query para evitar N+1
    unique_biz_ids = list({a.business_id for a in appointments})
    businesses = {
        b.id: b
        for b in db.query(Business).filter(Business.id.in_(unique_biz_ids)).all()
    }

    for appt in appointments:
        business = businesses.get(appt.business_id)
        if not business:
            # Appointment huérfano: loguear, limpiar notification_sent_at, continuar
            logger.warning("send_reminders: negocio no encontrado para appointment %s", appt.id)
            log_entry = ReminderLog(
                appointment_id=appt.id,
                business_id=appt.business_id,
                status="failed",
                channel="whatsapp_text",
                error_reason="business_not_found",
            )
            db.add(log_entry)
            appt.notification_sent_at = None  # con synchronize_session='fetch' esto funciona
            results["skipped"] += 1
            continue

        # Validar que el teléfono tenga formato E.164 antes de intentar cualquier envío
        phone_error = _validate_phone(appt.user_phone)
        if phone_error:
            log_entry = ReminderLog(
                appointment_id=appt.id,
                business_id=appt.business_id,
                status="failed",
                channel="whatsapp_text",
                error_reason=phone_error,
            )
            db.add(log_entry)
            appt.notification_sent_at = None
            results["skipped"] += 1
            logger.warning(
                "send_reminders: teléfono inválido (%s) para appt %s", phone_error, appt.id
            )
            continue

        # status="pending" indica que aún no se procesó — se actualiza en cada nivel
        log_entry = ReminderLog(
            appointment_id=appt.id,
            business_id=appt.business_id,
            status="pending",
            channel="whatsapp_text",
        )
        current_channel = "whatsapp_text"  # se actualiza en cada nivel

        # Savepoint: aísla cada iteración. Si falla, solo se revierte este appointment.
        try:
            with db.begin_nested():
                # Nivel 1: Templates pagos
                if business.use_whatsapp_templates:
                    await _send_template_reminder(appt, business)
                    log_entry.status = "sent"
                    log_entry.channel = "whatsapp_template"
                    current_channel = "whatsapp_template"
                    results["sent"] += 1

                # Nivel 2: Ventana 24h
                elif _within_24h_window(db, appt):
                    await send_message(
                        phone=appt.user_phone,
                        text=f"Recordatorio: tenés un turno mañana a las {appt.scheduled_date.strftime('%H:%M')}.",
                    )
                    log_entry.status = "sent"
                    log_entry.channel = "whatsapp_text"
                    current_channel = "whatsapp_text"
                    results["sent"] += 1

                # Nivel 3: Canal alternativo
                elif _has_alternative_channel(business):
                    log_entry.status = "outside_window"
                    log_entry.channel = "sms"
                    current_channel = "sms"
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

                # Solo loggear evento y marcar notification_sent_at si se envió
                if log_entry.status == "sent":
                    log_event(
                        session_id=appt.session_id or str(appt.user_phone),
                        business_id=appt.business_id,
                        event_type=EventType.REMINDER_SENT.value,
                        payload={
                            "appointment_id": appt.id,
                            "channel": log_entry.channel,
                        },
                    )
                    # Marcar como notificado para que no se reintente
                    appt.notification_sent_at = datetime.now(timezone.utc)
                else:
                    # No se envió — limpiar notification_sent_at para reintento
                    appt.notification_sent_at = None

                db.add(log_entry)
                # El savepoint hace commit automático al salir del with

        except Exception as e:
            logger.exception("send_reminders: error para appointment %s", appt.id)
            # El savepoint hizo rollback y el objeto log_entry quedó detached.
            # Creamos uno nuevo en vez de reusarlo para no depender del
            # comportamiento implícito de re-attachment de SQLAlchemy.
            failed_log = ReminderLog(
                appointment_id=appt.id,
                business_id=appt.business_id,
                status="failed",
                channel=current_channel,
                error_reason=str(e)[:500],
            )
            appt.notification_sent_at = None  # limpiar para reintento
            db.add(failed_log)
            results["failed"] += 1

    return results


def _within_24h_window(db, appointment) -> bool:
    """Verifica si el cliente está dentro de la ventana de 24h de WhatsApp.

    Solo aplica a sesiones de WhatsApp — las sesiones de web chat u otros
    canales no tienen restricción de ventana de 24h y retornan True.

    Solo eventos ENTRANTES del cliente (CONVERSATION_STARTED, MENU_OPTION_SELECTED,
    SERVICE_SELECTED, FALLBACK_TRIGGERED, REMINDER_RESPONSE) califican para
    resetear la ventana. Los eventos del bot (REMINDER_SENT, etc.) se excluyen
    para evitar falsos positivos que violarían la política de WhatsApp.

    Si session_id es None, no hay forma de verificar la ventana → False.
    """
    if appointment.session_id is None:
        return False

    # Si la sesión no tiene eventos de WhatsApp, es web chat u otro canal
    # sin restricción de ventana de 24h → permitir envío
    has_whatsapp = (
        db.query(Event.id)
        .filter(
            Event.business_id == appointment.business_id,
            Event.session_id == appointment.session_id,
            Event.channel == "whatsapp",
        )
        .limit(1)
        .first()
    ) is not None
    if not has_whatsapp:
        return True
    # Solo eventos iniciados por el cliente — los del bot NO resetean la ventana
    _USER_EVENT_TYPES = [
        EventType.CONVERSATION_STARTED.value,
        EventType.MENU_OPTION_SELECTED.value,
        EventType.SERVICE_SELECTED.value,
        EventType.FALLBACK_TRIGGERED.value,
        EventType.REMINDER_RESPONSE.value,
    ]
    last_message = (
        db.query(func.max(Event.timestamp))
        .filter(
            Event.business_id == appointment.business_id,
            Event.session_id == appointment.session_id,
            Event.channel == "whatsapp",
            Event.event_type.in_(_USER_EVENT_TYPES),
        )
        .scalar()
    )
    if not last_message:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    return last_message >= cutoff


def _has_alternative_channel(business) -> bool:
    """Verifica si el negocio tiene un canal alternativo para notificar
    al cliente cuando no se puede usar WhatsApp (fuera de ventana 24h).

    Revisa los flags sms_enabled y email_enabled del modelo Business.
    Si ambos están en False, Level 3 delega a Level 4 (notify owner).
    """
    return bool(
        getattr(business, "sms_enabled", False)
        or getattr(business, "email_enabled", False)
    )


async def _send_template_reminder(appointment, business) -> None:
    """Envía recordatorio usando template de WhatsApp."""
    await send_message(
        phone=appointment.user_phone,
        text=f"Recordatorio: {business.name} te espera mañana a las {appointment.scheduled_date.strftime('%H:%M')}.",
    )
