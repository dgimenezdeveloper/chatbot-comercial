"""Servicio de orquestación del chatbot — lógica de negocio conectada a DB.

Provee funciones auxiliares que el webhook usa para resolver servicios,
disponibilidad, usuarios y datos del negocio desde PostgreSQL.
"""

import logging
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


def get_available_slots(
    db: Session, service_id: int, business_id: int, target_date: date
) -> list[datetime]:
    """Calcula los slots disponibles para un servicio en una fecha.

    Retorna una lista de horarios (datetime) en los que el servicio está libre,
    considerando los turnos ya agendados para esa fecha.
    """
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.business_id == business_id)
        .first()
    )
    if not service:
        return []

    # Horario laboral: 09:00 a 20:00
    start_hour = 9
    end_hour = 20
    duration = service.duration_minutes or 30

    # Turnos ya ocupados en esa fecha
    occupied = (
        db.query(Appointment.scheduled_date)
        .filter(
            Appointment.business_id == business_id,
            Appointment.service_id == service_id,
            Appointment.scheduled_date >= datetime.combine(target_date, datetime.min.time()),
            Appointment.scheduled_date < datetime.combine(target_date, datetime.max.time()),
            Appointment.status.notin_([\"cancelled\"]),
        )
        .all()
    )
    occupied_times = {o[0] for o in occupied}

    slots = []
    current = datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour)
    end = current.replace(hour=end_hour)

    while current + timedelta(minutes=duration) <= end:
        if current not in occupied_times:
            slots.append(current)
        current += timedelta(minutes=duration)

    return slots


def get_business_timezone(db: Session, business_id: int) -> str:
    """Retorna el timezone configurado para un negocio."""
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.timezone if business else "America/Argentina/Buenos_Aires"
