"""Queries de métricas MVP — 12 funciones de consulta SQL aggregates.

Opera sobre las tablas ``event``, ``appointment``, ``session`` y ``feedback``
para calcular indicadores de rendimiento del chatbot con umbrales de alerta.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.service import Service
from app.db.models.appointment import Appointment
from app.db.models.events import Event
from app.db.models.sessions import ChatSession
from app.db.models.feedback import Feedback

logger = logging.getLogger(__name__)

THRESHOLDS: dict[str, dict[str, float]] = {
    "conversion_rate": {"warning": 0.20, "critical": 0.10},
    "bot_autonomy_rate": {"warning": 0.40, "critical": 0.25},
    "abandonment_rate": {"warning": 0.30, "critical": 0.40},
    "fallback_rate": {"warning": 0.15, "critical": 0.25},
    "nocturnal_appointment_rate": {"warning": 0.30, "critical": 0.10},
    "autonomous_resolution_rate": {"warning": 0.70, "critical": 0.50},
    "cancellation_rate": {"warning": 0.15, "critical": 0.20},
    "no_show_rate": {"warning": 0.10, "critical": 0.15},
    "reminder_confirmation_rate": {"warning": 0.60, "critical": 0.50},
    "csat_average": {"warning": 4.0, "critical": 3.5},
}


def _status(value: float, metric_name: str, higher_is_better: bool = False) -> str:
    """Determina el estado (ok/warning/critical) respecto a umbrales."""
    thresholds = THRESHOLDS.get(metric_name)
    if not thresholds:
        return "ok"
    warning = thresholds["warning"]
    critical = thresholds["critical"]
    if higher_is_better:
        if value >= warning:
            return "ok"
        if value >= critical:
            return "warning"
        return "critical"
    else:
        if value <= warning:
            return "ok"
        if value <= critical:
            return "warning"
        return "critical"


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


# ---------------------------------------------------------------------------
# M1 — Tasa de conversión inicio → turno
# ---------------------------------------------------------------------------

def get_conversion_rate(db: Session, business_id: int, days: int = 30) -> dict:
    starts = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "conversation_started",
            Event.timestamp >= _since(days),
        )
        .scalar()
    )
    appointments = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "appointment_created",
            Event.timestamp >= _since(days),
        )
        .scalar()
    )
    rate = appointments / starts if starts else 0.0
    return {
        "starts": starts,
        "appointments": appointments,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["conversion_rate"]["warning"] * 100,
        "status": _status(rate, "conversion_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M2 — % turnos creados por bot
# ---------------------------------------------------------------------------

def get_bot_autonomy_rate(db: Session, business_id: int, days: int = 30) -> dict:
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    bot = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_via == "chatbot",
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    rate = bot / total if total else 0.0
    return {
        "bot_appointments": bot,
        "total_appointments": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["bot_autonomy_rate"]["warning"] * 100,
        "status": _status(rate, "bot_autonomy_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M3 — Tasa de abandono por paso
# ---------------------------------------------------------------------------

def get_abandonment_rate(db: Session, business_id: int, days: int = 30) -> dict:
    total = (
        db.query(func.count(ChatSession.id))
        .filter(
            ChatSession.business_id == business_id,
            ChatSession.started_at >= _since(days),
        )
        .scalar()
    )
    abandoned = (
        db.query(func.count(ChatSession.id))
        .filter(
            ChatSession.business_id == business_id,
            ChatSession.status == "abandoned",
            ChatSession.started_at >= _since(days),
        )
        .scalar()
    )
    rate = abandoned / total if total else 0.0
    return {
        "abandoned_sessions": abandoned,
        "total_sessions": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["abandonment_rate"]["warning"] * 100,
        "status": _status(rate, "abandonment_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M4 — Tasa de fallback
# ---------------------------------------------------------------------------

def get_fallback_rate(db: Session, business_id: int, days: int = 30) -> dict:
    since = _since(days)
    fallbacks = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "fallback_triggered",
            Event.timestamp >= since,
        )
        .scalar()
    )
    interactions = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type.in_(
                ["menu_option_selected", "service_selected", "fallback_triggered"]
            ),
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = fallbacks / interactions if interactions else 0.0
    return {
        "fallback_events": fallbacks,
        "total_interactions": interactions,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["fallback_rate"]["warning"] * 100,
        "status": _status(rate, "fallback_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M5 — Top 10 mensajes con fallback
# ---------------------------------------------------------------------------

def get_top_fallback_messages(db: Session, business_id: int, days: int = 30) -> dict:
    rows = (
        db.query(
            Event.payload_json["message_original"].astext.label("message"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == "fallback_triggered",
            Event.timestamp >= _since(days),
        )
        .group_by(Event.payload_json["message_original"].astext)
        .order_by(func.count(Event.id).desc())
        .limit(10)
        .all()
    )
    messages = [{"message": row.message or "", "count": row.count} for row in rows]
    return {
        "messages": messages,
        "value": len(messages),
        "threshold": None,
        "status": "ok",
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M6 — % turnos nocturnos (20-8hs)
# ---------------------------------------------------------------------------

def get_nocturnal_appointment_rate(db: Session, business_id: int, days: int = 30) -> dict:
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    nocturnal = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
            func.extract("hour", Appointment.scheduled_date).in_(
                list(range(20, 24)) + list(range(0, 8))
            ),
        )
        .scalar()
    )
    rate = nocturnal / total if total else 0.0
    return {
        "nocturnal_appointments": nocturnal,
        "total_appointments": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["nocturnal_appointment_rate"]["warning"] * 100,
        "status": _status(rate, "nocturnal_appointment_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M7 — Tasa de resolución autónoma
# ---------------------------------------------------------------------------

def get_autonomous_resolution_rate(db: Session, business_id: int, days: int = 30) -> dict:
    since = _since(days)
    appointments = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "appointment_created",
            Event.timestamp >= since,
        )
        .scalar()
    )
    escalations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "escalation_to_human",
            Event.timestamp >= since,
        )
        .scalar()
    )
    total = appointments + escalations
    rate = appointments / total if total else 0.0
    return {
        "autonomous_resolutions": appointments,
        "total_resolutions": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["autonomous_resolution_rate"]["warning"] * 100,
        "status": _status(rate, "autonomous_resolution_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M8 — Tasa de cancelación
# ---------------------------------------------------------------------------

def get_cancellation_rate(db: Session, business_id: int, days: int = 30) -> dict:
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    rate = cancelled / total if total else 0.0
    return {
        "cancelled_appointments": cancelled,
        "total_appointments": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["cancellation_rate"]["warning"] * 100,
        "status": _status(rate, "cancellation_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M9 — Tasa de no-show
# ---------------------------------------------------------------------------

def get_no_show_rate(db: Session, business_id: int, days: int = 30) -> dict:
    total_with_reminder = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.no_show_status.isnot(None),
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    no_shows = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.no_show_status == "confirmed_no",
            Appointment.created_at >= _since(days),
        )
        .scalar()
    )
    rate = no_shows / total_with_reminder if total_with_reminder else 0.0
    return {
        "no_shows": no_shows,
        "total_with_reminder": total_with_reminder,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["no_show_rate"]["warning"] * 100,
        "status": _status(rate, "no_show_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M10 — Confirmación de recordatorio
# ---------------------------------------------------------------------------

def get_reminder_confirmation_rate(db: Session, business_id: int, days: int = 30) -> dict:
    since = _since(days)
    total = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "reminder_response",
            Event.timestamp >= since,
        )
        .scalar()
    )
    confirmations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == "reminder_response",
            Event.payload_json["response_type"].astext == "confirmo",
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = confirmations / total if total else 0.0
    return {
        "confirmations": confirmations,
        "total_reminders": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["reminder_confirmation_rate"]["warning"] * 100,
        "status": _status(rate, "reminder_confirmation_rate"),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M11 — Servicios más reservados
# ---------------------------------------------------------------------------

def get_top_services(db: Session, business_id: int, days: int = 30, limit: int = 10) -> dict:
    rows = (
        db.query(
            Appointment.service_id,
            Service.name.label("service_name"),
            func.count(Appointment.id).label("count"),
        )
        .join(Service, Appointment.service_id == Service.id)
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .group_by(Appointment.service_id, Service.name)
        .order_by(func.count(Appointment.id).desc())
        .limit(limit)
        .all()
    )
    services = [
        {"service_id": row.service_id, "service_name": row.service_name, "count": row.count}
        for row in rows
    ]
    return {
        "services": services,
        "value": len(services),
        "threshold": None,
        "status": "ok",
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# M12 — CSAT promedio
# ---------------------------------------------------------------------------

def get_csat_average(db: Session, business_id: int, days: int = 30) -> dict:
    result = (
        db.query(
            func.avg(Feedback.score).label("avg"),
            func.min(Feedback.score).label("min"),
            func.max(Feedback.score).label("max"),
            func.count(Feedback.id).label("total"),
        )
        .filter(
            Feedback.business_id == business_id,
            Feedback.submitted_at >= _since(days),
        )
        .first()
    )
    avg = float(result.avg) if result and result.avg else 0.0
    return {
        "average_score": round(avg, 2),
        "min_score": result.min if result and result.min else 0,
        "max_score": result.max if result and result.max else 0,
        "total_feedbacks": result.total if result else 0,
        "value": round(avg, 2),
        "threshold": THRESHOLDS["csat_average"]["warning"],
        "status": _status(avg, "csat_average", higher_is_better=True),
        "period": f"{days}d",
    }


# ---------------------------------------------------------------------------
# Agregador — todas las métricas en una sola llamada
# ---------------------------------------------------------------------------

def get_all_metrics(db: Session, business_id: int, days: int = 30) -> dict:
    """Retorna las 12 métricas MVP para un negocio en un solo dict."""
    return {
        "business_id": business_id,
        "period": f"{days}d",
        "conversion_rate": get_conversion_rate(db, business_id, days),
        "bot_autonomy_rate": get_bot_autonomy_rate(db, business_id, days),
        "abandonment_rate": get_abandonment_rate(db, business_id, days),
        "fallback_rate": get_fallback_rate(db, business_id, days),
        "top_fallback_messages": get_top_fallback_messages(db, business_id, days),
        "nocturnal_appointment_rate": get_nocturnal_appointment_rate(db, business_id, days),
        "autonomous_resolution_rate": get_autonomous_resolution_rate(db, business_id, days),
        "cancellation_rate": get_cancellation_rate(db, business_id, days),
        "no_show_rate": get_no_show_rate(db, business_id, days),
        "reminder_confirmation_rate": get_reminder_confirmation_rate(db, business_id, days),
        "top_services": get_top_services(db, business_id, days),
        "csat_average": get_csat_average(db, business_id, days),
    }
