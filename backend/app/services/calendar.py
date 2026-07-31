"""Servicio CRUD para gestión de turnos (appointments).

Operaciones contra PostgreSQL usando SQLAlchemy Session.
Sincronización automática con Google Calendar.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.db.models.service import Service
from app.services.google_calendar import create_event, delete_event

logger = logging.getLogger(__name__)


def create_appointment(db: Session, data: dict) -> Appointment:
    """Crea un nuevo turno, lo persiste y lo sincroniza con Google Calendar."""
    appointment = Appointment(**data)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Sincronización con Google Calendar
    try:
        business = db.query(Business).filter(Business.id == appointment.business_id).first()
        service = db.query(Service).filter(Service.id == appointment.service_id).first()
        
        if business and business.google_calendar_id and service:
            end_time = appointment.scheduled_date + timedelta(minutes=service.duration_minutes or 30)
            summary = f"Turno: {appointment.user_name} - {service.name}"
            desc = f"Teléfono: {appointment.user_phone}\nServicio: {service.name}\nGenerado por Pymebot"
            
            event_id = create_event(
                calendar_id=business.google_calendar_id,
                summary=summary,
                description=desc,
                start_time=appointment.scheduled_date,
                end_time=end_time
            )
            
            if event_id:
                appointment.google_event_id = event_id
                db.commit()
    except Exception as e:
        logger.error(f"Fallo al sincronizar turno {appointment.id} con Google Calendar: {e}")

    logger.info(
        "Turno creado: id=%s business_id=%s service_id=%s date=%s",
        appointment.id,
        appointment.business_id,
        appointment.service_id,
        appointment.scheduled_date,
    )
    return appointment


def get_appointments_by_date(
    db: Session, business_id: int, target_date: date
) -> list[Appointment]:
    """Lista todos los turnos de un negocio para una fecha específica."""
    return (
        db.query(Appointment)
        .filter(
            Appointment.business_id == business_id,
            Appointment.scheduled_date >= datetime.combine(target_date, datetime.min.time()),
            Appointment.scheduled_date < datetime.combine(target_date, datetime.max.time()),
        )
        .order_by(Appointment.scheduled_date)
        .all()
    )


def get_appointments_by_week(
    db: Session, business_id: int, start_date: date
) -> list[Appointment]:
    """Lista turnos de un negocio en la semana comenzando en start_date."""
    end_date = start_date + timedelta(days=7)
    return (
        db.query(Appointment)
        .filter(
            Appointment.business_id == business_id,
            Appointment.scheduled_date >= datetime.combine(start_date, datetime.min.time()),
            Appointment.scheduled_date < datetime.combine(end_date, datetime.min.time()),
        )
        .order_by(Appointment.scheduled_date)
        .all()
    )


def get_appointment(
    db: Session, appointment_id: int, business_id: int
) -> Optional[Appointment]:
    """Obtiene un turno por ID, validando pertenencia al negocio."""
    return (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.business_id == business_id,
        )
        .first()
    )


def get_appointments_by_phone(
    db: Session, business_id: int, user_phone: str
) -> list[Appointment]:
    """Lista todos los turnos de un cliente por su teléfono ordenados cronológicamente."""
    return (
        db.query(Appointment)
        .filter(
            Appointment.business_id == business_id,
            Appointment.user_phone == user_phone,
        )
        .order_by(Appointment.scheduled_date.asc())
        .all()
    )


def cancel_appointment(
    db: Session, appointment_id: int, business_id: int, reason: str
) -> Optional[Appointment]:
    """Cancela un turno guardando el motivo y lo elimina de Google Calendar."""
    appointment = get_appointment(db, appointment_id, business_id)
    if not appointment:
        return None
    appointment.status = "cancelled"
    appointment.cancelled_reason = reason
    appointment.cancellation_scheduled_date = appointment.scheduled_date
    
    # Eliminar de Google Calendar
    try:
        business = db.query(Business).filter(Business.id == business_id).first()
        if business and business.google_calendar_id and getattr(appointment, 'google_event_id', None):
            delete_event(business.google_calendar_id, appointment.google_event_id)
    except Exception as e:
        logger.error(f"Fallo al eliminar turno {appointment.id} de Google Calendar: {e}")

    db.commit()
    db.refresh(appointment)
    logger.info("Turno cancelado: id=%s reason=%s", appointment.id, reason)
    return appointment


def update_appointment_status(
    db: Session, appointment_id: int, business_id: int, status: str
) -> Optional[Appointment]:
    """Actualiza el estado de un turno (scheduled/confirmed/in_progress/completed/cancelled)."""
    appointment = get_appointment(db, appointment_id, business_id)
    if not appointment:
        return None
    appointment.status = status
    db.commit()
    db.refresh(appointment)
    logger.info("Turno actualizado: id=%s status=%s", appointment.id, status)
    return appointment