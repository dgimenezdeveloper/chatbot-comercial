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
from app.services.google_calendar import get_freebusy

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


def get_available_slots(
    db: Session, service_id: int, business_id: int, target_date: date
) -> list[datetime]:
    """Calcula los slots disponibles cruzando DB local y Google Calendar."""
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.business_id == business_id)
        .first()
    )
    business = db.query(Business).filter(Business.id == business_id).first()
    
    if not service or not business:
        return []

    tz_str = business.timezone or "America/Argentina/Buenos_Aires"
    tz = zoneinfo.ZoneInfo(tz_str)

    start_hour = 9
    end_hour = 20
    duration = service.duration_minutes or 30

    # Límites del día con timezone
    day_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=tz)
    day_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=tz)

    # 1. Turnos ya ocupados en DB
    occupied = (
        db.query(Appointment.scheduled_date)
        .filter(
            Appointment.business_id == business_id,
            Appointment.service_id == service_id,
            Appointment.scheduled_date >= day_start,
            Appointment.scheduled_date < day_end,
            Appointment.status.notin_(["cancelled"]),
        )
        .all()
    )
    # Convertir a timezone local para comparación exacta
    occupied_times = {o[0].astimezone(tz) for o in occupied}

    # 2. Consultar Google Calendar
    gcal_busy_slots = []
    if business.google_calendar_id:
        gcal_busy_slots = get_freebusy(business.google_calendar_id, day_start, day_end)

    slots = []
    current = day_start.replace(hour=start_hour)
    end = day_start.replace(hour=end_hour)

    while current + timedelta(minutes=duration) <= end:
        slot_end = current + timedelta(minutes=duration)
        is_free = True

        # Verificar DB local
        if current in occupied_times:
            is_free = False

        # Verificar Google Calendar (solapamiento de rangos)
        if is_free:
            for busy_start, busy_end in gcal_busy_slots:
                # Convertir a timezone local por si la API devuelve UTC
                busy_start_tz = busy_start.astimezone(tz)
                busy_end_tz = busy_end.astimezone(tz)
                
                # Hay solapamiento si el inicio del slot es menor al fin del evento ocupado
                # Y el fin del slot es mayor al inicio del evento ocupado
                if current < busy_end_tz and slot_end > busy_start_tz:
                    is_free = False
                    break

        if is_free:
            slots.append(current)

        current += timedelta(minutes=duration)

    return slots


def get_business_timezone(db: Session, business_id: int) -> str:
    """Retorna el timezone configurado para un negocio."""
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.timezone if business else "America/Argentina/Buenos_Aires"