"""Servicio de orquestación del chatbot — lógica de negocio conectada a DB.

Provee funciones auxiliares que el webhook usa para resolver servicios,
disponibilidad, usuarios y datos del negocio desde PostgreSQL y Google Calendar.
"""

import logging
import zoneinfo
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.db.models.service import Service
from app.db.models.user import User

logger = logging.getLogger(__name__)


def get_business_by_slug(db: Session, slug: str) -> Optional[Business]:
    """Busca un negocio por su slug único."""
    return db.query(Business).filter(Business.slug == slug, Business.active.is_(True)).first()


def get_business_by_phone(db: Session, phone_id: str) -> Optional[Business]:
    """Busca un negocio por su WhatsApp Phone ID."""
    return (
        db.query(Business)
        .filter(Business.whatsapp_phone_id == phone_id, Business.active.is_(True))
        .first()
    )


def get_or_create_user(db: Session, phone: str, business_id: int, name: str = "") -> User:
    """Busca un usuario por teléfono; si no existe, crea uno con rol guest."""
    user = (
        db.query(User)
        .filter(User.phone == phone, User.business_id == business_id)
        .first()
    )
    if user:
        return user

    user = User(
        business_id=business_id,
        phone=phone,
        name=name or f"Cliente {phone[-4:]}",
        role="guest",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Usuario guest creado: id=%s phone=%s", user.id, phone)
    return user


def get_active_services(db: Session, business_id: int) -> list[Service]:
    """Lista los servicios activos de un negocio (para mostrar en el menú del chatbot)."""
    return (
        db.query(Service)
        .filter(Service.business_id == business_id, Service.is_active.is_(True))
        .order_by(Service.category, Service.name)
        .all()
    )


def get_business_timezone(db: Session, business_id: int) -> str:
    """Retorna el timezone configurado para un negocio."""
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.timezone if business else "America/Argentina/Buenos_Aires"


def get_available_slots(
    db: Session, service_id: int, business_id: int, target_date: date
) -> list[datetime]:
    """Calcula los slots disponibles para un servicio en una fecha sin superposiciones.

    Garantiza que un único profesional (un solo cliente a la vez) no tenga turnos solapados,
    considerando la duración del servicio solicitado y los turnos existentes.
    """
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.business_id == business_id)
        .first()
    )
    if not service:
        return []

    # Horario laboral habitual (09:00 a 20:00)
    start_hour = 9
    end_hour = 20
    duration = service.duration_minutes or 30

    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)

    start_dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=tz)
    end_dt = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=tz)

    # 1. Obtener todos los turnos agendados en esa fecha junto con la duración de su servicio
    existing_appointments = (
        db.query(Appointment.scheduled_date, Service.duration_minutes)
        .join(Service, Appointment.service_id == Service.id)
        .filter(
            Appointment.business_id == business_id,
            Appointment.scheduled_date >= start_dt,
            Appointment.scheduled_date <= end_dt,
            Appointment.status.notin_(["cancelled"]),
        )
        .all()
    )

    # Construir la lista de franjas de tiempo completamente ocupadas [inicio, fin)
    occupied_intervals: list[tuple[datetime, datetime]] = []
    for appt_date, appt_duration in existing_appointments:
        b_start = appt_date.astimezone(tz)
        b_end = b_start + timedelta(minutes=appt_duration or 30)
        occupied_intervals.append((b_start, b_end))

    # 2. Incluir franjas ocupadas en Google Calendar (si está configurado)
    business = db.query(Business).filter(Business.id == business_id).first()
    if business and business.google_calendar_id:
        try:
            from app.services.google_calendar import get_busy_slots
            gcal_busy = get_busy_slots(business.google_calendar_id, start_dt, end_dt)
            for g_start, g_end in gcal_busy:
                occupied_intervals.append((g_start.astimezone(tz), g_end.astimezone(tz)))
        except Exception as e:
            logger.error(f"Error consultando Google Calendar (se continúa con slots locales): {e}")

    slots = []
    current = start_dt.replace(hour=start_hour)
    day_end = start_dt.replace(hour=end_hour)

    # 3. Iterar cada slot posible y validar colisiones de intervalos de tiempo
    while current + timedelta(minutes=duration) <= day_end:
        slot_start = current
        slot_end = current + timedelta(minutes=duration)
        
        is_free = True
        for occ_start, occ_end in occupied_intervals:
            # Condición matemática de solapamiento de intervalos
            if (slot_start < occ_end) and (slot_end > occ_start):
                is_free = False
                break

        if is_free:
            slots.append(current)

        current += timedelta(minutes=duration)

    return slots