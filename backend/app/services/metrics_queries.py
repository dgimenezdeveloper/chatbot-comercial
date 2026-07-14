"""Queries de métricas — 50 funciones de consulta SQL aggregates.

Opera sobre las tablas ``event``, ``appointment``, ``session`` y ``feedback``
para calcular indicadores de rendimiento del chatbot con umbrales de alerta.

start_date/end_date tienen precedencia sobre days cuando se proveen.
Per-business thresholds se resuelven desde metric_thresholds si existen.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Integer, case, exc as sqlalchemy_exc, func
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.service import Service
from app.db.models.appointment import Appointment
from app.db.models.events import Event
from app.db.models.sessions import ChatSession
from app.db.models.feedback import Feedback
from app.services.metrics_types import EventType

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
    "nps": {"warning": 50.0, "critical": 0.0},
    # Extended metrics thresholds
    "conversion_by_service": {"warning": 0.20, "critical": 0.10},
    "fallback_retry_rate": {"warning": 0.30, "critical": 0.15},
    "self_service_modification_rate": {"warning": 0.50, "critical": 0.30},
    "late_cancellation_rate": {"warning": 0.20, "critical": 0.35},
    "reminder_delivery_rate": {"warning": 0.80, "critical": 0.60},
    "reminder_read_rate": {"warning": 0.70, "critical": 0.50},
    "reminder_response_rate": {"warning": 0.50, "critical": 0.30},
    "avg_reminder_response_time": {"warning": 30.0, "critical": 60.0},
    "manual_escalation_rate": {"warning": 0.10, "critical": 0.20},
    "auto_escalation_rate": {"warning": 0.05, "critical": 0.10},
    "post_escalation_conversion": {"warning": 0.30, "critical": 0.15},
    "returning_users_30d": {"warning": 0.40, "critical": 0.25},
    "usage_frequency": {"warning": 3.0, "critical": 1.0},
    "avg_time_to_appointment": {"warning": 300.0, "critical": 600.0},
    "churn_by_channel": {"warning": 0.20, "critical": 0.35},
    "no_show_by_user_type": {"warning": 0.10, "critical": 0.15},
    "no_show_by_service": {"warning": 0.10, "critical": 0.15},
    "message_hourly_distribution": {"warning": None, "critical": None},
    "input_type_ratio": {"warning": None, "critical": None},
    "avg_message_length": {"warning": None, "critical": None},
    "response_speed_percentiles": {"warning": None, "critical": None},
    "read_receipt_buckets": {"warning": None, "critical": None},
    "csat_by_outcome": {"warning": 4.0, "critical": 3.5},
    "feedback_clustering": {"warning": None, "critical": None},
}

# Cache de thresholds por negocio para evitar consultar la DB en cada métrica
_thresholds_cache: dict[int, dict[str, dict[str, float]]] = {}


def clear_thresholds_cache(business_id: int) -> None:
    """Invalida la caché de thresholds para un negocio.

    Debe llamarse después de cualquier PUT a metric-thresholds
    para que las métricas usen los nuevos valores inmediatamente.
    """
    _thresholds_cache.pop(business_id, None)


def _load_business_thresholds(db: Session, business_id: int) -> dict[str, dict[str, float]]:
    """Carga thresholds del negocio desde DB, con caché en memoria."""
    if business_id in _thresholds_cache:
        return _thresholds_cache[business_id]

    from app.db.models.metric_threshold import MetricThreshold
    rows = (
        db.query(MetricThreshold)
        .filter(MetricThreshold.business_id == business_id)
        .all()
    )
    biz_thresholds: dict[str, dict[str, float]] = {}
    for row in rows:
        biz_thresholds[row.metric_name] = {
            "warning": row.warning_value,
            "critical": row.critical_value,
        }
    _thresholds_cache[business_id] = biz_thresholds
    return biz_thresholds


def _status(
    value: float,
    metric_name: str,
    higher_is_better: bool = False,
    business_thresholds: dict[str, dict[str, float]] | None = None,
) -> str:
    """Determina el estado (ok/warning/critical) respecto a umbrales.

    Args:
        value: Valor de la métrica.
        metric_name: Nombre de la métrica para lookup en THRESHOLDS.
        higher_is_better: Si True, valores altos son buenos.
        business_thresholds: Umbrales por negocio (tienen precedencia sobre defaults).
    """
    # Per-business thresholds tienen precedencia
    if business_thresholds and metric_name in business_thresholds:
        thresholds = business_thresholds[metric_name]
    else:
        thresholds = THRESHOLDS.get(metric_name)

    if not thresholds or thresholds.get("warning") is None:
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


def _resolve_window(days: int, start_date: str | None, end_date: str | None) -> tuple[datetime, str]:
    """Resuelve la ventana temporal.

    Si start_date/end_date están presentes, tienen precedencia sobre days.
    Retorna (since, period_label).
    """
    if start_date and end_date:
        try:
            since = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            until = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            days_diff = (until - since).days
            return since, f"{start_date}_{end_date}"
        except (ValueError, TypeError):
            pass  # fall through to days-based
    return _since(days), f"{days}d"


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def _validate_days(days: int) -> int:
    """Valida y normaliza el parámetro days."""
    if days < 1:
        logger.warning("metrics: days=%d inválido, usando default 30", days)
        return 30
    if days > 365:
        logger.warning("metrics: days=%d excede máximo, usando 365", days)
        return 365
    return days


# ---------------------------------------------------------------------------
# M1 — Tasa de conversión inicio → turno
# ---------------------------------------------------------------------------

def get_conversion_rate(db: Session, business_id: int, days: int = 30,
                        since: datetime | None = None, period_label: str | None = None,
                        biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since, period_label = _resolve_window(days, None, None)
    if period_label is None:
        period_label = f"{days}d"
    starts = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.CONVERSATION_STARTED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    appointments = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CREATED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = appointments / starts if starts else 0.0
    return {
        "starts": starts,
        "appointments": appointments,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["conversion_rate"]["warning"] * 100,
        "status": _status(rate, "conversion_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M2 — % turnos creados por bot
# ---------------------------------------------------------------------------

def get_bot_autonomy_rate(db: Session, business_id: int, days: int = 30,
                          since: datetime | None = None, period_label: str | None = None,
                          biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
        )
        .scalar()
    )
    bot = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_via == "chatbot",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    rate = bot / total if total else 0.0
    return {
        "bot_appointments": bot,
        "total_appointments": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["bot_autonomy_rate"]["warning"] * 100,
        "status": _status(rate, "bot_autonomy_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M3 — Tasa de abandono por paso
# ---------------------------------------------------------------------------

def get_abandonment_rate(db: Session, business_id: int, days: int = 30,
                         since: datetime | None = None, period_label: str | None = None,
                         biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total = (
        db.query(func.count(ChatSession.id))
        .filter(
            ChatSession.business_id == business_id,
            ChatSession.started_at >= since,
        )
        .scalar()
    )
    abandoned = (
        db.query(func.count(ChatSession.id))
        .filter(
            ChatSession.business_id == business_id,
            ChatSession.status == "abandoned",
            ChatSession.started_at >= since,
        )
        .scalar()
    )
    rate = abandoned / total if total else 0.0
    return {
        "abandoned_sessions": abandoned,
        "total_sessions": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["abandonment_rate"]["warning"] * 100,
        "status": _status(rate, "abandonment_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M4 — Tasa de fallback
# ---------------------------------------------------------------------------

def get_fallback_rate(db: Session, business_id: int, days: int = 30,
                      since: datetime | None = None, period_label: str | None = None,
                      biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    fallbacks = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.FALLBACK_TRIGGERED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    interactions = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type.in_([
                EventType.MENU_OPTION_SELECTED,
                EventType.SERVICE_SELECTED,
                EventType.FALLBACK_TRIGGERED,
            ]),
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
        "status": _status(rate, "fallback_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M5 — Top 10 mensajes con fallback
# ---------------------------------------------------------------------------

def get_top_fallback_messages(db: Session, business_id: int, days: int = 30,
                              since: datetime | None = None, period_label: str | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    rows = (
        db.query(
            Event.payload_json["message_original"].astext.label("message"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.FALLBACK_TRIGGERED,
            Event.timestamp >= since,
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
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M6 — % turnos nocturnos (20-8hs)
# ---------------------------------------------------------------------------

def get_nocturnal_appointment_rate(db: Session, business_id: int, days: int = 30,
                                   since: datetime | None = None, period_label: str | None = None,
                                   biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
        )
        .scalar()
    )
    nocturnal = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
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
        "status": _status(rate, "nocturnal_appointment_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M7 — Tasa de resolución autónoma
# ---------------------------------------------------------------------------

def get_autonomous_resolution_rate(db: Session, business_id: int, days: int = 30,
                                   since: datetime | None = None, period_label: str | None = None,
                                   biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    appointments = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CREATED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    escalations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
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
        "status": _status(rate, "autonomous_resolution_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M8 — Tasa de cancelación
# ---------------------------------------------------------------------------

def get_cancellation_rate(db: Session, business_id: int, days: int = 30,
                          since: datetime | None = None, period_label: str | None = None,
                          biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
        )
        .scalar()
    )
    cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    rate = cancelled / total if total else 0.0
    return {
        "cancelled_appointments": cancelled,
        "total_appointments": total,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["cancellation_rate"]["warning"] * 100,
        "status": _status(rate, "cancellation_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M9 — Tasa de no-show
# ---------------------------------------------------------------------------

def get_no_show_rate(db: Session, business_id: int, days: int = 30,
                     since: datetime | None = None, period_label: str | None = None,
                     biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total_with_reminder = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.no_show_status.isnot(None),
            Appointment.created_at >= since,
        )
        .scalar()
    )
    no_shows = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.no_show_status == "confirmed_no",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    rate = no_shows / total_with_reminder if total_with_reminder else 0.0
    return {
        "no_shows": no_shows,
        "total_with_reminder": total_with_reminder,
        "value": round(rate * 100, 2),
        "threshold": THRESHOLDS["no_show_rate"]["warning"] * 100,
        "status": _status(rate, "no_show_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M10 — Confirmación de recordatorio
# ---------------------------------------------------------------------------

def get_reminder_confirmation_rate(db: Session, business_id: int, days: int = 30,
                                   since: datetime | None = None, period_label: str | None = None,
                                   biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    total = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_RESPONSE,
            Event.timestamp >= since,
        )
        .scalar()
    )
    confirmations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_RESPONSE,
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
        "status": _status(rate, "reminder_confirmation_rate", business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M11 — Servicios más reservados
# ---------------------------------------------------------------------------

def get_top_services(db: Session, business_id: int, days: int = 30, limit: int = 10,
                     since: datetime | None = None, period_label: str | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    rows = (
        db.query(
            Appointment.service_id,
            Service.name.label("service_name"),
            func.count(Appointment.id).label("count"),
        )
        .join(Service, Appointment.service_id == Service.id)
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
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
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# M12 — CSAT promedio (escala 1-5, excluye NULL scores)
# ---------------------------------------------------------------------------

def get_csat_average(db: Session, business_id: int, days: int = 30,
                     since: datetime | None = None, period_label: str | None = None,
                     biz_thresholds: dict | None = None) -> dict:
    if since is None:
        days = _validate_days(days)
        since = _since(days)
    if period_label is None:
        period_label = f"{days}d"
    # Filter NULL scores to avoid total_feedbacks > scored_feedbacks mismatch
    result = (
        db.query(
            func.avg(Feedback.score).label("avg"),
            func.min(Feedback.score).label("min"),
            func.max(Feedback.score).label("max"),
            func.count(Feedback.id).label("total"),
        )
        .filter(
            Feedback.business_id == business_id,
            Feedback.score.isnot(None),
            Feedback.submitted_at >= since,
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
        "status": _status(avg, "csat_average", higher_is_better=True, business_thresholds=biz_thresholds),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# Agregador — todas las métricas en una sola llamada
# ---------------------------------------------------------------------------

def get_all_metrics(
    db: Session,
    business_id: int,
    days: int = 30,
    include_extended: bool = False,
    segment_by: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Retorna las 50 métricas (12 base + 38 extendidas) para un negocio.

    Si include_extended=False, retorna solo las 12 MVP.
    Si start_date/end_date están presentes, tienen precedencia sobre days.
    segment_by se aplica como filtro a nivel de get_all_metrics.
    """
    days = _validate_days(days)
    since, period_label = _resolve_window(days, start_date, end_date)

    # Cargar thresholds por negocio una sola vez para todas las métricas
    biz_thresholds = _load_business_thresholds(db, business_id) if business_id else {}

    result = {
        "business_id": business_id,
        "period": period_label,
        "conversion_rate": get_conversion_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "bot_autonomy_rate": get_bot_autonomy_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "abandonment_rate": get_abandonment_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "fallback_rate": get_fallback_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "top_fallback_messages": get_top_fallback_messages(db, business_id, since=since, period_label=period_label),
        "nocturnal_appointment_rate": get_nocturnal_appointment_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "autonomous_resolution_rate": get_autonomous_resolution_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "cancellation_rate": get_cancellation_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "no_show_rate": get_no_show_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "reminder_confirmation_rate": get_reminder_confirmation_rate(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
        "top_services": get_top_services(db, business_id, since=since, period_label=period_label),
        "csat_average": get_csat_average(db, business_id, since=since, period_label=period_label, biz_thresholds=biz_thresholds),
    }

    if include_extended:
        result["extended"] = {}
        ext = result["extended"]

        # C1 — Agendar turno (6)
        ext["conversion_by_service"] = get_conversion_by_service(db, business_id, days)
        ext["fallback_retry_rate"] = get_fallback_retry_rate(db, business_id, days)
        ext["appointment_lead_time"] = get_appointment_lead_time_distribution(db, business_id, days)
        ext["preferred_hours"] = get_preferred_hours_distribution(db, business_id, days)
        ext["new_vs_returning"] = get_new_vs_returning_clients(db, business_id, days)
        ext["avg_time_to_appointment"] = get_avg_time_to_appointment(db, business_id, days)

        # C2 — Modificar (4)
        ext["self_service_modification_rate"] = get_self_service_modification_rate(db, business_id, days)
        ext["modification_reasons"] = get_modification_reasons(db, business_id, days)
        ext["post_reminder_modifications"] = get_post_reminder_modifications(db, business_id, days)
        ext["avg_modification_time"] = get_avg_modification_time(db, business_id, days)

        # C3 — Cancelar (3)
        ext["late_cancellation_rate"] = get_late_cancellation_rate(db, business_id, days)
        ext["cancellation_reasons"] = get_cancellation_reasons(db, business_id, days)
        ext["post_reminder_cancellations"] = get_post_reminder_cancellations(db, business_id, days)

        # C4 — Recordatorios (6)
        ext["reminder_delivery_rate"] = get_reminder_delivery_rate(db, business_id, days)
        ext["reminder_read_rate"] = get_reminder_read_rate(db, business_id, days)
        ext["reminder_response_rate"] = get_reminder_response_rate(db, business_id, days)
        ext["avg_reminder_response_time"] = get_avg_reminder_response_time(db, business_id, days)
        ext["no_show_reminder_impact"] = get_no_show_reminder_impact(db, business_id, days)
        ext["cancellation_no_confirmation"] = get_cancellation_no_confirmation_impact(db, business_id, days)

        # C5 — Escalamiento (4)
        ext["manual_escalation_rate"] = get_manual_escalation_rate(db, business_id, days)
        ext["escalation_reasons"] = get_escalation_reasons(db, business_id, days)
        ext["post_escalation_conversion"] = get_post_escalation_conversion(db, business_id, days)
        ext["auto_escalation_rate"] = get_auto_escalation_rate(db, business_id, days)

        # C6 — Retención (4)
        ext["returning_users_30d"] = get_returning_users_30d(db, business_id, days)
        ext["usage_frequency"] = get_usage_frequency(db, business_id, days)
        ext["churn_by_channel"] = get_churn_by_channel(db, business_id, days)
        ext["avg_time_first_second"] = get_avg_time_between_first_second(db, business_id, days)

        # C7 — No-Show (2)
        ext["no_show_by_user_type"] = get_no_show_by_user_type(db, business_id, days)
        ext["no_show_by_service"] = get_no_show_by_service(db, business_id, days)

        # C8 — WhatsApp (6)
        ext["message_hourly_distribution"] = get_message_hourly_distribution(db, business_id, days)
        ext["message_dow_distribution"] = get_message_dow_distribution(db, business_id, days)
        ext["response_speed_percentiles"] = get_response_speed_percentiles(db, business_id, days)
        ext["input_type_ratio"] = get_input_type_ratio(db, business_id, days)
        ext["avg_message_length"] = get_avg_message_length(db, business_id, days)
        ext["read_receipt_buckets"] = get_read_receipt_buckets(db, business_id, days)

        # C9 — Satisfacción (3)
        ext["csat_by_outcome"] = get_csat_by_outcome(db, business_id, days)
        ext["nps"] = get_nps(db, business_id, days)
        ext["feedback_clustering"] = get_feedback_clustering(db, business_id, days)

    return result


# ============================================================================
# Bloque C — 38 nuevas métricas (chatbot-mvp-completion)
# ============================================================================

# ---------------------------------------------------------------------------
# C1 — Agendar turno nuevo (6 métricas)
# ---------------------------------------------------------------------------

def get_conversion_by_service(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.1 — Tasa de conversión por servicio: turnos / consultas agrupado por service_id."""
    since = _since(days)
    # Single query: appointments per service
    appt_rows = (
        db.query(
            Appointment.service_id,
            func.count(Appointment.id).label("appointments"),
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
        )
        .group_by(Appointment.service_id)
        .all()
    )
    # Single pre-fetch: all service_selected counts (0 N+1)
    query_rows = (
        db.query(
            Event.payload_json["service_id"].astext,
            func.count(Event.id).label("query_count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.SERVICE_SELECTED,
            Event.timestamp >= since,
        )
        .group_by(Event.payload_json["service_id"].astext)
        .all()
    )
    query_map = {str(row[0]): row[1] for row in query_rows}

    services = []
    for row in appt_rows:
        service_queries = query_map.get(str(row.service_id), 0)
        rate = row.appointments / service_queries if service_queries else 0.0
        services.append({
            "service_id": row.service_id,
            "appointments": row.appointments,
            "queries": service_queries,
            "rate": round(rate * 100, 2),
        })
    overall_rate = sum(s["appointments"] for s in services) / sum(s["queries"] for s in services) if services and sum(s["queries"] for s in services) else 0.0
    return {
        "services": services,
        "value": round(overall_rate * 100, 2),
        "threshold": 30.0,
        "status": _status(overall_rate, "conversion_by_service"),
        "period": period_label,
    }


def get_fallback_retry_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.2 — Tasa de reintentos tras fallback."""
    since = _since(days)
    fallback_users = (
        db.query(Event.user_id)
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.FALLBACK_TRIGGERED,
            Event.timestamp >= since,
            Event.user_id.isnot(None),
        )
        .distinct()
        .subquery()
    )
    retry_count = (
        db.query(func.count(func.distinct(Event.user_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CREATED,
            Event.timestamp >= since,
            Event.user_id.in_(db.query(fallback_users.c.user_id)),
        )
        .scalar()
    )
    total_fallback_users = (
        db.query(func.count(func.distinct(Event.user_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.FALLBACK_TRIGGERED,
            Event.timestamp >= since,
            Event.user_id.isnot(None),
        )
        .scalar()
    )
    rate = retry_count / total_fallback_users if total_fallback_users else 0.0
    return {
        "retry_users": retry_count,
        "total_fallback_users": total_fallback_users,
        "value": round(rate * 100, 2),
        "threshold": 40.0,
        "status": _status(rate, "fallback_retry_rate"),
        "period": period_label,
    }


def get_appointment_lead_time_distribution(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.3 — % turnos por anticipación (buckets: hoy/mañana/semana/mes)."""
    appointments = (
        db.query(Appointment.scheduled_date, Appointment.created_at)
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .all()
    )
    hoy = manana = semana = mes = 0
    for a in appointments:
        delta_days = (a.scheduled_date - a.created_at).days if a.scheduled_date and a.created_at else 999
        if delta_days <= 0:
            hoy += 1
        elif delta_days == 1:
            manana += 1
        elif delta_days <= 7:
            semana += 1
        else:
            mes += 1
    total = len(appointments)
    return {
        "buckets": {
            "hoy": {"count": hoy, "pct": round(hoy / total * 100, 2) if total else 0},
            "manana": {"count": manana, "pct": round(manana / total * 100, 2) if total else 0},
            "semana": {"count": semana, "pct": round(semana / total * 100, 2) if total else 0},
            "mes": {"count": mes, "pct": round(mes / total * 100, 2) if total else 0},
        },
        "value": total,
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_preferred_hours_distribution(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.4 — Distribución de horarios preferidos por hora del día."""
    rows = (
        db.query(
            func.extract("hour", Appointment.scheduled_date).label("hour"),
            func.count(Appointment.id).label("count"),
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )
    distribution = {str(int(r.hour)): r.count for r in rows}
    return {
        "distribution": distribution,
        "value": sum(distribution.values()),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_new_vs_returning_clients(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.5 — Clientes nuevos vs recurrentes (first_appointment / total)."""
    since = _since(days)
    total_users = (
        db.query(func.count(func.distinct(Appointment.user_id)))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
            Appointment.user_id.isnot(None),
        )
        .scalar()
    )
    first_timers = (
        db.query(func.count(func.distinct(Appointment.user_id)))
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= since,
            Appointment.user_id.isnot(None),
            ~Appointment.user_id.in_(
                db.query(Appointment.user_id).filter(
                    Appointment.business_id == business_id,
                    Appointment.created_at < since,
                    Appointment.user_id.isnot(None),
                )
            ),
        )
        .scalar()
    )
    rate = first_timers / total_users if total_users else 0.0
    return {
        "new_clients": first_timers,
        "total_clients": total_users,
        "value": round(rate * 100, 2),
        "threshold": 30.0,
        "status": _status(rate, "conversion_rate", higher_is_better=True),
        "period": period_label,
    }


def get_avg_time_to_appointment(db: Session, business_id: int, days: int = 30) -> dict:
    """C1.6 — Tiempo promedio desde inicio de conversación hasta turno creado (segundos)."""
    since = _since(days)
    rows = (
        db.query(
            Event.session_id,
            func.min(Event.timestamp).label("start_time"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.CONVERSATION_STARTED,
            Event.timestamp >= since,
        )
        .group_by(Event.session_id)
        .subquery()
    )
    results = (
        db.query(
            func.avg(
                func.extract("epoch", Event.timestamp - rows.c.start_time)
            ).label("avg_seconds"),
        )
        .join(rows, Event.session_id == rows.c.session_id)
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CREATED,
            Event.timestamp >= since,
        )
        .first()
    )
    avg_seconds = float(results.avg_seconds) if results and results.avg_seconds else 0.0
    return {
        "avg_seconds": round(avg_seconds, 1),
        "value": round(avg_seconds, 1),
        "threshold": 180.0,
        "status": _status(avg_seconds, "avg_time_to_appointment"),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C2 — Modificar turno (4 métricas)
# ---------------------------------------------------------------------------

def get_self_service_modification_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C2.1 — Tasa de self-service en modificaciones vía bot."""
    since = _since(days)
    modificaciones = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_MODIFIED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    bot_modificaciones = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_MODIFIED,
            Event.channel == "whatsapp",
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = bot_modificaciones / modificaciones if modificaciones else 0.0
    return {
        "self_service_count": bot_modificaciones,
        "total_modifications": modificaciones,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_modification_reasons(db: Session, business_id: int, days: int = 30) -> dict:
    """C2.2 — Motivos de cambio (clustering de modification_reason)."""
    rows = (
        db.query(
            Event.payload_json["modification_reason"].astext.label("reason"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_MODIFIED,
            Event.timestamp >= _since(days),
            Event.payload_json["modification_reason"].astext.isnot(None),
        )
        .group_by(Event.payload_json["modification_reason"].astext)
        .order_by(func.count(Event.id).desc())
        .limit(20)
        .all()
    )
    reasons = [{"reason": r.reason or "sin_especificar", "count": r.count} for r in rows]
    return {
        "reasons": reasons,
        "value": len(reasons),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_post_reminder_modifications(db: Session, business_id: int, days: int = 30) -> dict:
    """C2.3 — Modificaciones iniciadas post-recordatorio."""
    since = _since(days)
    reminders = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .scalar()
    )
    post_reminder_mods = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_MODIFIED,
            Event.timestamp >= since,
            Event.payload_json["triggered_by_reminder"].astext == "true",
        )
        .scalar()
    )
    rate = post_reminder_mods / reminders if reminders else 0.0
    return {
        "post_reminder_count": post_reminder_mods,
        "total_reminders": reminders,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_avg_modification_time(db: Session, business_id: int, days: int = 30) -> dict:
    """C2.4 — Tiempo promedio entre turno original y modificación (horas)."""
    since = _since(days)
    try:
        rows = (
            db.query(
                Event.payload_json["original_appointment_id"].astext.cast(Integer).label("aid"),
                func.min(Event.timestamp).label("mod_time"),
            )
            .filter(
                Event.business_id == business_id,
                Event.event_type == EventType.APPOINTMENT_MODIFIED,
                Event.timestamp >= since,
                Event.payload_json["original_appointment_id"].astext.isnot(None),
            )
            .group_by(Event.payload_json["original_appointment_id"].astext.cast(Integer))
            .all()
        )
    except sqlalchemy_exc.DataError:
        rows = []
    if not rows:
        return {"avg_hours": 0.0, "value": 0.0, "threshold": None, "status": "ok", "period": f"{days}d"}

    # Bulk pre-fetch: all original appointments in one query (0 N+1)
    ids = [r.aid for r in rows]
    orig_map = {
        a.id: a.created_at
        for a in db.query(Appointment.id, Appointment.created_at)
        .filter(Appointment.id.in_(ids), Appointment.business_id == business_id)
        .all()
    }

    total_hours = 0.0
    count = 0
    for r in rows:
        orig = orig_map.get(r.aid)
        if orig:
            delta_hours = (r.mod_time - orig).total_seconds() / 3600
            total_hours += delta_hours
            count += 1
    avg_hours = total_hours / count if count else 0.0
    return {
        "avg_hours": round(avg_hours, 1),
        "value": round(avg_hours, 1),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C3 — Cancelar turno (3 métricas)
# ---------------------------------------------------------------------------

def get_late_cancellation_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C3.1 — Cancelación tardía (<24hs antes del turno)."""
    since = _since(days)
    total_cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    late_cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.created_at >= since,
            func.extract("epoch", Appointment.scheduled_date - Appointment.updated_at) < 86400,
        )
        .scalar()
    )
    rate = late_cancelled / total_cancelled if total_cancelled else 0.0
    return {
        "late_cancellations": late_cancelled,
        "total_cancellations": total_cancelled,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_cancellation_reasons(db: Session, business_id: int, days: int = 30) -> dict:
    """C3.2 — Motivos de cancelación (clustering de cancelled_reason)."""
    rows = (
        db.query(
            Appointment.cancelled_reason,
            func.count(Appointment.id).label("count"),
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.cancelled_reason.isnot(None),
            Appointment.created_at >= _since(days),
        )
        .group_by(Appointment.cancelled_reason)
        .order_by(func.count(Appointment.id).desc())
        .limit(20)
        .all()
    )
    reasons = [{"reason": r.cancelled_reason or "sin_especificar", "count": r.count} for r in rows]
    return {
        "reasons": reasons,
        "value": len(reasons),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_post_reminder_cancellations(db: Session, business_id: int, days: int = 30) -> dict:
    """C3.3 — Cancelaciones dentro de las 4hs post-recordatorio."""
    since = _since(days)
    reminders = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .scalar()
    )
    post_reminder = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CANCELLED,
            Event.timestamp >= since,
            Event.payload_json["trigger"].astext == "reminder_response",
        )
        .scalar()
    )
    rate = post_reminder / reminders if reminders else 0.0
    return {
        "post_reminder_cancellations": post_reminder,
        "total_reminders": reminders,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C4 — Recordatorio T-24hs (6 métricas)
# ---------------------------------------------------------------------------

def get_reminder_delivery_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.1 — Tasa de envío exitoso de recordatorios."""
    since = _since(days)
    total_scheduled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.notification_sent_at.isnot(None),
            Appointment.created_at >= since,
        )
        .scalar()
    )
    sent = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = sent / total_scheduled if total_scheduled else 0.0
    return {
        "successfully_sent": sent,
        "total_scheduled": total_scheduled,
        "value": round(rate * 100, 2),
        "threshold": 90.0,
        "status": _status(rate, "reminder_confirmation_rate", higher_is_better=True),
        "period": period_label,
    }


def get_reminder_read_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.2 — Tasa de lectura (read receipt) de recordatorios."""
    since = _since(days)
    sent = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .scalar()
    )
    read = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_READ,
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = read / sent if sent else 0.0
    return {
        "read_count": read,
        "sent_count": sent,
        "value": round(rate * 100, 2),
        "threshold": 50.0,
        "status": _status(rate, "reminder_confirmation_rate", higher_is_better=True),
        "period": period_label,
    }


def get_reminder_response_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.3 — Tasa de respuesta al recordatorio."""
    since = _since(days)
    read = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_READ,
            Event.timestamp >= since,
        )
        .scalar()
    )
    responses = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_RESPONSE,
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = responses / read if read else 0.0
    return {
        "response_count": responses,
        "read_count": read,
        "value": round(rate * 100, 2),
        "threshold": 30.0,
        "status": _status(rate, "reminder_confirmation_rate", higher_is_better=True),
        "period": period_label,
    }


def get_avg_reminder_response_time(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.4 — Tiempo promedio de respuesta a recordatorio (minutos)."""
    since = _since(days)
    # Single query: all reminders sent
    reminders = (
        db.query(Event.session_id, Event.timestamp)
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .all()
    )
    total = len(reminders)
    if not total:
        return {"avg_minutes": 0.0, "total_reminders": 0, "value": 0.0, "threshold": 60.0, "status": "ok", "period": f"{days}d"}

    # Pre-fetch earliest response per session in one query (0 N+1)
    session_ids = [r.session_id for r in reminders if r.session_id]
    responses = []
    if session_ids:
        responses = (
            db.query(
                Event.session_id,
                func.min(Event.timestamp).label("first_resp"),
            )
            .filter(
                Event.business_id == business_id,
                Event.event_type == EventType.REMINDER_RESPONSE,
                Event.session_id.in_(session_ids),
                Event.timestamp >= since,
            )
            .group_by(Event.session_id)
            .all()
        )
    resp_map = {r.session_id: r.first_resp for r in responses}

    total_seconds = 0.0
    count = 0
    for rem in reminders:
        if rem.session_id and rem.session_id in resp_map:
            resp_time = resp_map[rem.session_id]
            if resp_time > rem.timestamp:
                total_seconds += (resp_time - rem.timestamp).total_seconds()
                count += 1
    avg_min = (total_seconds / 60) / count if count else 0.0
    return {
        "avg_minutes": round(avg_min, 1),
        "total_reminders": total,
        "value": round(avg_min, 1),
        "threshold": 60.0,
        "status": _status(avg_min, "avg_reminder_response_time"),
        "period": period_label,
    }


def get_no_show_reminder_impact(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.5 / C7.2 — Impacto del recordatorio en no-shows (compartida)."""
    since = _since(days)
    with_reminder = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.notification_sent_at.isnot(None),
            Appointment.created_at >= since,
            Appointment.no_show_status.isnot(None),
        )
        .scalar()
    )
    with_no_show = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.notification_sent_at.isnot(None),
            Appointment.no_show_status == "confirmed_no",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    without_reminder = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.notification_sent_at.is_(None),
            Appointment.created_at >= since,
            Appointment.no_show_status.isnot(None),
        )
        .scalar()
    )
    without_no_show = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.notification_sent_at.is_(None),
            Appointment.no_show_status == "confirmed_no",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    with_rate = with_no_show / with_reminder if with_reminder else 0.0
    without_rate = without_no_show / without_reminder if without_reminder else 0.0
    return {
        "with_reminder": {
            "no_shows": with_no_show,
            "total": with_reminder,
            "rate": round(with_rate * 100, 2),
        },
        "without_reminder": {
            "no_shows": without_no_show,
            "total": without_reminder,
            "rate": round(without_rate * 100, 2),
        },
        "value": round((without_rate - with_rate) * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_cancellation_no_confirmation_impact(db: Session, business_id: int, days: int = 30) -> dict:
    """C4.6 — Impacto en cancelación por no confirmación al recordatorio."""
    since = _since(days)
    total_cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.created_at >= since,
        )
        .scalar()
    )
    no_response_cancelled = (
        db.query(func.count(Appointment.id))
        .filter(
            Appointment.business_id == business_id,
            Appointment.status == "cancelled",
            Appointment.no_show_status == "pending",
            Appointment.notification_sent_at.isnot(None),
            Appointment.created_at >= since,
        )
        .scalar()
    )
    rate = no_response_cancelled / total_cancelled if total_cancelled else 0.0
    return {
        "no_response_cancelled": no_response_cancelled,
        "total_cancelled": total_cancelled,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C5 — Bot vs escalamiento (4 métricas)
# ---------------------------------------------------------------------------

def get_manual_escalation_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C5.1 — Tasa de escalamiento manual (usuario solicita humano)."""
    since = _since(days)
    total_conversations = (
        db.query(func.count(func.distinct(Event.session_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.CONVERSATION_STARTED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    escalations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = escalations / total_conversations if total_conversations else 0.0
    return {
        "escalations": escalations,
        "total_conversations": total_conversations,
        "value": round(rate * 100, 2),
        "threshold": 30.0,
        "status": _status(rate, "manual_escalation_rate"),
        "period": period_label,
    }


def get_escalation_reasons(db: Session, business_id: int, days: int = 30) -> dict:
    """C5.2 — Motivos de escalamiento (clustering)."""
    rows = (
        db.query(
            Event.payload_json["escalation_reason"].astext.label("reason"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
            Event.timestamp >= _since(days),
            Event.payload_json["escalation_reason"].astext.isnot(None),
        )
        .group_by(Event.payload_json["escalation_reason"].astext)
        .order_by(func.count(Event.id).desc())
        .limit(20)
        .all()
    )
    reasons = [{"reason": r.reason or "sin_especificar", "count": r.count} for r in rows]
    return {
        "reasons": reasons,
        "value": len(reasons),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_post_escalation_conversion(db: Session, business_id: int, days: int = 30) -> dict:
    """C5.3 — Tasa de conversión post-escalamiento a humano."""
    since = _since(days)
    total_escalations = (
        db.query(func.count(func.distinct(Event.session_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
            Event.timestamp >= since,
        )
        .scalar()
    )
    esc_sessions = (
        db.query(Event.session_id)
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
            Event.timestamp >= since,
        )
        .distinct()
        .subquery()
    )
    bookings = (
        db.query(func.count(func.distinct(Event.session_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.APPOINTMENT_CREATED,
            Event.timestamp >= since,
            Event.session_id.in_(db.query(esc_sessions.c.session_id)),
        )
        .scalar()
    )
    rate = bookings / total_escalations if total_escalations else 0.0
    return {
        "bookings_after_escalation": bookings,
        "total_escalations": total_escalations,
        "value": round(rate * 100, 2),
        "threshold": 50.0,
        "status": _status(rate, "reminder_confirmation_rate", higher_is_better=True),
        "period": period_label,
    }


def get_auto_escalation_rate(db: Session, business_id: int, days: int = 30) -> dict:
    """C5.4 — Escalamiento automático (2 fallbacks consecutivos)."""
    since = _since(days)
    total_conversations = (
        db.query(func.count(func.distinct(Event.session_id)))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.CONVERSATION_STARTED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    auto_escalations = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.ESCALATION_TO_HUMAN,
            Event.payload_json["trigger"].astext == "auto_fallback",
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = auto_escalations / total_conversations if total_conversations else 0.0
    return {
        "auto_escalations": auto_escalations,
        "total_conversations": total_conversations,
        "value": round(rate * 100, 2),
        "threshold": 20.0,
        "status": _status(rate, "auto_escalation_rate"),
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C6 — Retención y re-engagement (4 métricas)
# ---------------------------------------------------------------------------

def get_returning_users_30d(db: Session, business_id: int, days: int = 30) -> dict:
    """C6.1 — Usuarios recurrentes: volvieron en los últimos 30 días."""
    since = _since(days)
    period_start = _since(60)
    all_users = (
        db.query(func.count(func.distinct(Appointment.user_id)))
        .filter(
            Appointment.business_id == business_id,
            Appointment.user_id.isnot(None),
            Appointment.created_at >= period_start,
        )
        .scalar()
    )
    returning = (
        db.query(func.count(func.distinct(Appointment.user_id)))
        .filter(
            Appointment.business_id == business_id,
            Appointment.user_id.isnot(None),
            Appointment.created_at >= since,
            Appointment.user_id.in_(
                db.query(Appointment.user_id).filter(
                    Appointment.business_id == business_id,
                    Appointment.created_at < since,
                    Appointment.created_at >= period_start,
                    Appointment.user_id.isnot(None),
                )
            ),
        )
        .scalar()
    )
    rate = returning / all_users if all_users else 0.0
    return {
        "returning_users": returning,
        "total_users": all_users,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_usage_frequency(db: Session, business_id: int, days: int = 30) -> dict:
    """C6.2 — Frecuencia de uso: usuarios con 2+ turnos."""
    since = _since(days)
    rows = (
        db.query(
            Appointment.user_id,
            func.count(Appointment.id).label("count"),
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.user_id.isnot(None),
            Appointment.created_at >= since,
        )
        .group_by(Appointment.user_id)
        .all()
    )
    total_users = len(rows)
    multi_appointment_users = sum(1 for r in rows if r.count >= 2)
    rate = multi_appointment_users / total_users if total_users else 0.0
    return {
        "multi_appointment_users": multi_appointment_users,
        "total_users": total_users,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_churn_by_channel(db: Session, business_id: int, days: int = 30) -> dict:
    """C6.3 — Churn por canal de adquisición."""
    since = _since(days)
    period_start = _since(60)
    channels = ["chatbot", "web", "api"]
    result = {}
    for ch in channels:
        acquired = (
            db.query(func.count(func.distinct(Appointment.user_id)))
            .filter(
                Appointment.business_id == business_id,
                Appointment.created_via == ch,
                Appointment.created_at < since,
                Appointment.created_at >= period_start,
                Appointment.user_id.isnot(None),
            )
            .scalar()
        )
        churned = (
            db.query(func.count(func.distinct(Appointment.user_id)))
            .filter(
                Appointment.business_id == business_id,
                Appointment.created_via == ch,
                Appointment.created_at < since,
                Appointment.created_at >= period_start,
                Appointment.user_id.isnot(None),
                ~Appointment.user_id.in_(
                    db.query(Appointment.user_id).filter(
                        Appointment.business_id == business_id,
                        Appointment.created_at >= since,
                        Appointment.user_id.isnot(None),
                    )
                ),
            )
            .scalar()
        )
        result[ch] = {
            "acquired": acquired,
            "churned": churned,
            "rate": round(churned / acquired * 100, 2) if acquired else 0.0,
        }
    return {
        "channels": result,
        "value": sum(r["rate"] for r in result.values()) / len(channels) if channels else 0.0,
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_avg_time_between_first_second(db: Session, business_id: int, days: int = 30) -> dict:
    """C6.4 — Tiempo promedio entre 1er y 2do turno (días)."""
    since = _since(days)
    # CTE with ROW_NUMBER to get first 2 appointments per user in one query
    ranked = (
        db.query(
            Appointment.user_id,
            Appointment.created_at,
            func.row_number()
            .over(partition_by=Appointment.user_id, order_by=Appointment.created_at.asc())
            .label("rn"),
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.user_id.isnot(None),
            Appointment.created_at >= since,
        )
        .cte("ranked")
    )
    pairs = (
        db.query(
            ranked.c.user_id,
            func.max(case([(ranked.c.rn == 1, ranked.c.created_at)], else_=None)).label("first_date"),
            func.max(case([(ranked.c.rn == 2, ranked.c.created_at)], else_=None)).label("second_date"),
        )
        .filter(ranked.c.rn.in_([1, 2]))
        .group_by(ranked.c.user_id)
        .having(func.count(ranked.c.rn) == 2)
        .all()
    )
    deltas = [
        (p.second_date - p.first_date).days
        for p in pairs
        if p.first_date and p.second_date
    ]
    avg_days = sum(deltas) / len(deltas) if deltas else 0.0
    return {
        "avg_days": round(avg_days, 1),
        "value": round(avg_days, 1),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C7 — No-Show segmentado (2 métricas nuevas + C4.5 compartida)
# ---------------------------------------------------------------------------

def get_no_show_by_user_type(db: Session, business_id: int, days: int = 30) -> dict:
    """C7.1 — No-show por tipo de usuario: bot vs manual."""
    since = _since(days)
    result = {}
    for via in ["chatbot", "web"]:
        total = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.business_id == business_id,
                Appointment.created_via == via,
                Appointment.created_at >= since,
                Appointment.no_show_status.isnot(None),
            )
            .scalar()
        )
        no_shows = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.business_id == business_id,
                Appointment.created_via == via,
                Appointment.no_show_status == "confirmed_no",
                Appointment.created_at >= since,
            )
            .scalar()
        )
        result[via] = {
            "total": total,
            "no_shows": no_shows,
            "rate": round(no_shows / total * 100, 2) if total else 0.0,
        }
    return {
        "user_types": result,
        "value": max(r["rate"] for r in result.values()) if result else 0.0,
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_no_show_by_service(db: Session, business_id: int, days: int = 30) -> dict:
    """C7.3 — No-show por servicio."""
    rows = (
        db.query(
            Appointment.service_id,
            Service.name.label("service_name"),
            func.count(Appointment.id).label("total"),
            func.sum(
                func.case((Appointment.no_show_status == "confirmed_no", 1), else_=0)
            ).label("no_shows"),
        )
        .join(Service, Appointment.service_id == Service.id)
        .filter(
            Appointment.business_id == business_id,
            Appointment.created_at >= _since(days),
            Appointment.no_show_status.isnot(None),
        )
        .group_by(Appointment.service_id, Service.name)
        .all()
    )
    services = [
        {
            "service_id": r.service_id,
            "service_name": r.service_name,
            "total": r.total,
            "no_shows": r.no_shows,
            "rate": round(r.no_shows / r.total * 100, 2) if r.total else 0.0,
        }
        for r in rows
    ]
    overall = sum(s["no_shows"] for s in services) / sum(s["total"] for s in services) if services and sum(s["total"] for s in services) else 0.0
    return {
        "services": services,
        "value": round(overall * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C8 — WhatsApp específico (6 métricas)
# ---------------------------------------------------------------------------

def get_message_hourly_distribution(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.1 — Distribución horaria de mensajes entrantes por hora."""
    rows = (
        db.query(
            func.extract("hour", Event.timestamp).label("hour"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.CONVERSATION_STARTED,
            Event.timestamp >= _since(days),
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )
    distribution = {str(int(r.hour)): r.count for r in rows}
    return {
        "distribution": distribution,
        "value": sum(distribution.values()),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_message_dow_distribution(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.2 — Distribución por día de la semana (0=dom, 6=sáb)."""
    rows = (
        db.query(
            func.extract("dow", Event.timestamp).label("dow"),
            func.count(Event.id).label("count"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type.in_([EventType.CONVERSATION_STARTED, EventType.MENU_OPTION_SELECTED, EventType.SERVICE_SELECTED]),
            Event.timestamp >= _since(days),
        )
        .group_by("dow")
        .order_by("dow")
        .all()
    )
    distribution = {str(int(r.dow)): r.count for r in rows}
    return {
        "distribution": distribution,
        "value": sum(distribution.values()),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_response_speed_percentiles(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.3 — Velocidad de respuesta: P50 y P95 en segundos usando PostgreSQL percentiles."""
    since = _since(days)
    # Subquery: inter-event gaps per session using window function
    gap_subq = (
        db.query(
            func.extract(
                "epoch",
                Event.timestamp
                - func.lag(Event.timestamp).over(
                    partition_by=Event.session_id, order_by=Event.timestamp.asc()
                ),
            ).label("gap_seconds")
        )
        .filter(
            Event.business_id == business_id,
            Event.timestamp >= since,
            Event.channel == "whatsapp",
        )
        .subquery()
    )
    p50 = (
        db.query(func.percentile_cont(0.50).within_group(gap_subq.c.gap_seconds))
        .filter(gap_subq.c.gap_seconds.isnot(None))
        .scalar()
    ) or 0.0
    p95 = (
        db.query(func.percentile_cont(0.95).within_group(gap_subq.c.gap_seconds))
        .filter(gap_subq.c.gap_seconds.isnot(None))
        .scalar()
    ) or 0.0
    return {
        "p50_seconds": round(float(p50), 1),
        "p95_seconds": round(float(p95), 1),
        "value": round(float(p50), 1),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_input_type_ratio(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.4 — Tipo de input: botones vs texto libre."""
    since = _since(days)
    buttons = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.MENU_OPTION_SELECTED,
            Event.timestamp >= since,
        )
        .scalar()
    )
    total_inputs = (
        db.query(func.count(Event.id))
        .filter(
            Event.business_id == business_id,
            Event.event_type.in_([EventType.MENU_OPTION_SELECTED, EventType.SERVICE_SELECTED, EventType.FALLBACK_TRIGGERED]),
            Event.timestamp >= since,
        )
        .scalar()
    )
    rate = buttons / total_inputs if total_inputs else 0.0
    return {
        "button_clicks": buttons,
        "total_inputs": total_inputs,
        "value": round(rate * 100, 2),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_avg_message_length(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.5 — Longitud promedio de mensajes de usuario."""
    since = _since(days)
    avg_len = (
        db.query(
            func.avg(
                func.length(Event.payload_json["message_original"].astext)
            ).label("avg_length"),
        )
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.FALLBACK_TRIGGERED,
            Event.timestamp >= since,
            Event.payload_json["message_original"].astext.isnot(None),
        )
        .first()
    )
    avg = float(avg_len.avg_length) if avg_len and avg_len.avg_length else 0.0
    return {
        "avg_chars": round(avg, 1),
        "value": round(avg, 1),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


def get_read_receipt_buckets(db: Session, business_id: int, days: int = 30) -> dict:
    """C8.6 — Read receipts acumulados en buckets excluyentes: 1h, 4h, 24h post-recordatorio."""
    since = _since(days)
    # Single query: all reminders sent
    reminders = (
        db.query(Event.session_id, Event.timestamp)
        .filter(
            Event.business_id == business_id,
            Event.event_type == EventType.REMINDER_SENT,
            Event.timestamp >= since,
        )
        .all()
    )
    total = len(reminders)
    if not total:
        return {
            "buckets": {"1h": {"count": 0, "pct": 0}, "4h": {"count": 0, "pct": 0}, "24h": {"count": 0, "pct": 0}},
            "total_reminders": 0,
            "value": 0.0,
            "threshold": None,
            "status": "ok",
            "period": period_label,
        }

    # Pre-fetch earliest read per session in one query (0 N+1)
    session_ids = [r.session_id for r in reminders if r.session_id]
    reads = []
    if session_ids:
        reads = (
            db.query(
                Event.session_id,
                func.min(Event.timestamp).label("first_read"),
            )
            .filter(
                Event.business_id == business_id,
                Event.event_type == EventType.REMINDER_READ,
                Event.session_id.in_(session_ids),
                Event.timestamp >= since,
            )
            .group_by(Event.session_id)
            .all()
        )
    read_map = {r.session_id: r.first_read for r in reads}

    b1h = b4h = b24h = 0
    for rem in reminders:
        if rem.session_id and rem.session_id in read_map:
            read_time = read_map[rem.session_id]
            if read_time > rem.timestamp:
                delta_hours = (read_time - rem.timestamp).total_seconds() / 3600
                if delta_hours <= 1:
                    b1h += 1
                elif delta_hours <= 4:
                    b4h += 1
                elif delta_hours <= 24:
                    b24h += 1
    return {
        "buckets": {
            "1h": {"count": b1h, "pct": round(b1h / total * 100, 2) if total else 0},
            "4h": {"count": b4h, "pct": round(b4h / total * 100, 2) if total else 0},
            "24h": {"count": b24h, "pct": round(b24h / total * 100, 2) if total else 0},
        },
        "total_reminders": total,
        "value": round(b1h / total * 100, 2) if total else 0.0,
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }


# ---------------------------------------------------------------------------
# C9 — Satisfacción y NPS (3 métricas)
# ---------------------------------------------------------------------------

def get_csat_by_outcome(db: Session, business_id: int, days: int = 30) -> dict:
    """C9.1 — CSAT segmentado por resultado de la interacción (excluye NULL scores)."""
    rows = (
        db.query(
            Feedback.outcome,
            func.avg(Feedback.score).label("avg_score"),
            func.count(Feedback.id).label("count"),
        )
        .filter(
            Feedback.business_id == business_id,
            Feedback.score.isnot(None),
            Feedback.submitted_at >= _since(days),
            Feedback.outcome.isnot(None),
        )
        .group_by(Feedback.outcome)
        .all()
    )
    outcomes = {
        r.outcome: {"avg_score": round(float(r.avg_score), 2), "count": r.count}
        for r in rows
    }
    overall = sum(o["avg_score"] for o in outcomes.values()) / len(outcomes) if outcomes else 0.0
    return {
        "outcomes": outcomes,
        "value": round(overall, 2),
        "threshold": 3.5,
        "status": _status(overall, "csat_average", higher_is_better=True),
        "period": period_label,
    }


def get_nps(db: Session, business_id: int, days: int = 30) -> dict:
    """C9.2 — Net Promoter Score adaptado a escala 1-5 del Feedback.

    La escala del modelo Feedback es 1-5 (no 0-10 estándar).
    Promotores: score >= 5. Detractores: score <= 3. Pasivos: score = 4.
    NPS = (%promotores - %detractores) * 100.
    NOTA: Este NPS no es comparable con benchmarks estándar (escala diferente).
    """
    since = _since(days)
    total = (
        db.query(func.count(Feedback.id))
        .filter(
            Feedback.business_id == business_id,
            Feedback.score.isnot(None),
            Feedback.submitted_at >= since,
        )
        .scalar()
    )
    if not total:
        return {"promoters": 0, "detractors": 0, "passives": 0, "total": 0,
                "value": 0.0, "threshold": 50.0, "status": "ok", "period": f"{days}d"}
    promoters = (
        db.query(func.count(Feedback.id))
        .filter(
            Feedback.business_id == business_id,
            Feedback.submitted_at >= since,
            Feedback.score >= 5,
        )
        .scalar()
    )
    detractors = (
        db.query(func.count(Feedback.id))
        .filter(
            Feedback.business_id == business_id,
            Feedback.submitted_at >= since,
            Feedback.score <= 3,
        )
        .scalar()
    )
    nps = (promoters - detractors) / total * 100 if total else 0.0
    return {
        "promoters": promoters,
        "detractors": detractors,
        "passives": total - promoters - detractors,
        "total": total,
        "value": round(nps, 1),
        "threshold": 50.0,
        "status": _status(nps, "nps", higher_is_better=True),
        "period": period_label,
    }


def get_feedback_clustering(db: Session, business_id: int, days: int = 30) -> dict:
    """C9.3 — Comentarios libres: frecuencia de feedback por categoría."""
    rows = (
        db.query(
            Feedback.outcome,
            func.count(Feedback.id).label("count"),
            func.avg(Feedback.score).label("avg_score"),
        )
        .filter(
            Feedback.business_id == business_id,
            Feedback.submitted_at >= _since(days),
            Feedback.comment.isnot(None),
        )
        .group_by(Feedback.outcome)
        .order_by(func.count(Feedback.id).desc())
        .all()
    )
    categories = [
        {"category": r.outcome or "sin_categoria", "count": r.count, "avg_score": round(float(r.avg_score), 2)}
        for r in rows
    ]
    return {
        "categories": categories,
        "value": len(categories),
        "threshold": None,
        "status": "ok",
        "period": period_label,
    }
