"""Tipos y constantes compartidos para métricas."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class EventType(str, Enum):
    """Tipos de eventos registrados en la tabla Event."""
    CONVERSATION_STARTED = "conversation_started"
    APPOINTMENT_CREATED = "appointment_created"
    FALLBACK_TRIGGERED = "fallback_triggered"
    MENU_OPTION_SELECTED = "menu_option_selected"
    SERVICE_SELECTED = "service_selected"
    REMINDER_SENT = "reminder_sent"
    REMINDER_RESPONSE = "reminder_response"
    READ_RECEIPT = "read_receipt"
    ESCALATION_TO_HUMAN = "escalation_to_human"
    ESCALATION_AUTO = "escalation_auto"
    HUMAN_RESPONSE = "human_response"
    CONVERSATION_ENDED = "conversation_ended"
    APPOINTMENT_MODIFIED = "appointment_modified"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    NO_SHOW = "no_show"


class MetricResult(TypedDict, total=False):
    """Forma base de retorno para todas las métricas."""
    value: float
    threshold: float | None
    status: str
    period: str
