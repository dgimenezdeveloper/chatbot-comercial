"""Tipos y constantes compartidos para métricas."""

from __future__ import annotations

from enum import Enum


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
    REMINDER_READ = "reminder_read"
    NO_SHOW = "no_show"
