"""Schemas Pydantic para las 12 métricas MVP del chatbot.

Cada métrica incluye valor calculado, umbral de alerta, estado (ok/warning/critical)
y período de análisis.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class MetricResult(BaseModel):
    """Resultado base para una métrica individual."""

    value: float = Field(..., description="Valor calculado de la métrica")
    threshold: Optional[float] = Field(None, description="Umbral de alerta configurado")
    status: Literal["ok", "warning", "critical"] = Field(
        ..., description="Estado respecto al umbral"
    )
    period: str = Field(default="30d", description="Período de análisis (ej: 7d, 30d)")


class ConversionRate(MetricResult):
    """M1 — Tasa de conversión inicio → turno (%)."""

    starts: int = Field(..., description="Cantidad de conversaciones iniciadas")
    appointments: int = Field(..., description="Cantidad de turnos creados")


class BotAutonomyRate(MetricResult):
    """M2 — % de turnos creados por el bot."""

    bot_appointments: int = Field(..., description="Turnos creados por chatbot")
    total_appointments: int = Field(..., description="Total de turnos creados")


class AbandonmentRate(MetricResult):
    """M3 — Tasa de abandono por paso (%)."""

    abandoned_sessions: int = Field(..., description="Sesiones abandonadas")
    total_sessions: int = Field(..., description="Total de sesiones")


class FallbackRate(MetricResult):
    """M4 — Tasa de fallback (%)."""

    fallback_events: int = Field(..., description="Cantidad de fallbacks")
    total_interactions: int = Field(..., description="Interacciones totales consideradas")


class TopFallbackMessage(BaseModel):
    """Fila individual del ranking de mensajes con más fallbacks."""

    message: str = Field(..., description="Texto del mensaje original")
    count: int = Field(..., description="Cantidad de fallbacks para este mensaje")


class TopFallbackMessages(MetricResult):
    """M5 — Top 10 mensajes con más fallbacks."""

    messages: list[TopFallbackMessage] = Field(
        default_factory=list, description="Ranking de mensajes con fallback"
    )


class NocturnalAppointmentRate(MetricResult):
    """M6 — % de turnos en horario nocturno (20-8hs)."""

    nocturnal_appointments: int = Field(..., description="Turnos nocturnos")
    total_appointments: int = Field(..., description="Total de turnos")


class AutonomousResolutionRate(MetricResult):
    """M7 — Tasa de resolución autónoma (sin escalar a humano)."""

    autonomous_resolutions: int = Field(..., description="Resoluciones sin escalamiento")
    total_resolutions: int = Field(..., description="Total de resoluciones")


class CancellationRate(MetricResult):
    """M8 — Tasa de cancelación de turnos (%)."""

    cancelled_appointments: int = Field(..., description="Turnos cancelados")
    total_appointments: int = Field(..., description="Total de turnos")


class NoShowRate(MetricResult):
    """M9 — Tasa de no-show (%)."""

    no_shows: int = Field(..., description="Cantidad de no-shows")
    total_with_reminder: int = Field(..., description="Turnos con recordatorio enviado")


class ReminderConfirmationRate(MetricResult):
    """M10 — Tasa de confirmación de recordatorios (%)."""

    confirmations: int = Field(..., description="Respuestas de confirmación")
    total_reminders: int = Field(..., description="Total de recordatorios enviados")


class TopService(BaseModel):
    """Fila individual del ranking de servicios más reservados."""

    service_id: int = Field(..., description="ID del servicio")
    service_name: str = Field(..., description="Nombre del servicio")
    count: int = Field(..., description="Cantidad de reservas")


class TopServices(MetricResult):
    """M11 — Ranking de servicios más reservados."""

    services: list[TopService] = Field(
        default_factory=list, description="Ranking de servicios"
    )


class CSATAverage(MetricResult):
    """M12 — CSAT promedio (1-5)."""

    average_score: float = Field(..., description="Puntaje promedio")
    min_score: int = Field(..., description="Puntaje mínimo")
    max_score: int = Field(..., description="Puntaje máximo")
    total_feedbacks: int = Field(..., description="Cantidad total de calificaciones")


class ExtendedMetricResult(BaseModel):
    """Resultado genérico para métricas extendidas (38 nuevas).

    Cada métrica retorna sus campos específicos en un dict.
    """

    value: float = Field(default=0.0, description="Valor calculado")
    threshold: Optional[float] = Field(None, description="Umbral de alerta")
    status: Literal["ok", "warning", "critical"] = Field(
        default="ok", description="Estado respecto al umbral"
    )
    period: str = Field(default="30d", description="Período de análisis")
    data: dict = Field(default_factory=dict, description="Datos adicionales de la métrica")


class AllMetrics(BaseModel):
    """Agregado de las 50 métricas (12 MVP + 38 extendidas) para un negocio."""

    business_id: int = Field(..., description="ID del negocio")
    period: str = Field(default="30d", description="Período de análisis")
    conversion_rate: Optional[ConversionRate] = None
    bot_autonomy_rate: Optional[BotAutonomyRate] = None
    abandonment_rate: Optional[AbandonmentRate] = None
    fallback_rate: Optional[FallbackRate] = None
    top_fallback_messages: Optional[TopFallbackMessages] = None
    nocturnal_appointment_rate: Optional[NocturnalAppointmentRate] = None
    autonomous_resolution_rate: Optional[AutonomousResolutionRate] = None
    cancellation_rate: Optional[CancellationRate] = None
    no_show_rate: Optional[NoShowRate] = None
    reminder_confirmation_rate: Optional[ReminderConfirmationRate] = None
    top_services: Optional[TopServices] = None
    csat_average: Optional[CSATAverage] = None
    extended: Optional[dict[str, ExtendedMetricResult]] = Field(
        None, description="38 métricas extendidas (solo cuando include_extended=true)"
    )

    model_config = ConfigDict(from_attributes=True)
