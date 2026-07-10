"""Tests para los 12 schemas de métricas Pydantic + AllMetrics."""

import pytest
from pydantic import ValidationError

from app.schemas.metrics import (
    AllMetrics,
    AutonomousResolutionRate,
    BotAutonomyRate,
    CancellationRate,
    ConversionRate,
    CSATAverage,
    FallbackRate,
    MetricResult,
    NocturnalAppointmentRate,
    NoShowRate,
    ReminderConfirmationRate,
    TopFallbackMessage,
    TopFallbackMessages,
    TopService,
    TopServices,
)


# ============================================================================
# MetricResult (base)
# ============================================================================

class TestMetricResult:
    """Validación del schema base MetricResult."""

    def test_valid_minimal(self):
        """Creación con campos mínimos requeridos."""
        m = MetricResult(value=75.5, status="ok")
        assert m.value == 75.5
        assert m.threshold is None
        assert m.status == "ok"
        assert m.period == "30d"

    def test_valid_with_threshold(self):
        """Con threshold explícito."""
        m = MetricResult(value=75.5, threshold=20.0, status="ok", period="7d")
        assert m.threshold == 20.0
        assert m.period == "7d"

    def test_invalid_status_rejected(self):
        """Status inválido debe fallar."""
        with pytest.raises(ValidationError):
            MetricResult(value=50, status="invalid_status")  # type: ignore[arg-type]

    def test_valid_status_ok(self):
        assert MetricResult(value=10, status="ok").status == "ok"

    def test_valid_status_warning(self):
        assert MetricResult(value=10, status="warning").status == "warning"

    def test_valid_status_critical(self):
        assert MetricResult(value=10, status="critical").status == "critical"

    def test_missing_value_raises(self):
        with pytest.raises(ValidationError):
            MetricResult(status="ok")  # type: ignore[arg-type]

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            MetricResult(value=50)  # type: ignore[arg-type]


# ============================================================================
# ConversionRate (M1)
# ============================================================================

class TestConversionRate:
    def test_valid(self):
        m = ConversionRate(value=45.0, status="ok", starts=100, appointments=45)
        assert m.starts == 100
        assert m.appointments == 45
        assert m.value == 45.0

    def test_zero_starts(self):
        m = ConversionRate(value=0.0, status="critical", starts=0, appointments=0)
        assert m.starts == 0

    def test_missing_starts_raises(self):
        with pytest.raises(ValidationError):
            ConversionRate(value=0.0, status="ok", appointments=0)  # type: ignore[arg-type]

    def test_missing_appointments_raises(self):
        with pytest.raises(ValidationError):
            ConversionRate(value=0.0, status="ok", starts=0)  # type: ignore[arg-type]


# ============================================================================
# BotAutonomyRate (M2)
# ============================================================================

class TestBotAutonomyRate:
    def test_valid(self):
        m = BotAutonomyRate(value=80.0, status="ok", bot_appointments=80, total_appointments=100)
        assert m.bot_appointments == 80
        assert m.total_appointments == 100

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            BotAutonomyRate(value=0.0, status="ok", total_appointments=0)  # type: ignore[arg-type]


# ============================================================================
# AbandonmentRate (M3)
# ============================================================================

class TestAbandonmentRate:
    def test_valid(self):
        m = AbandonmentRate(value=25.0, status="ok", abandoned_sessions=5, total_sessions=20)
        assert m.abandoned_sessions == 5
        assert m.total_sessions == 20


# ============================================================================
# FallbackRate (M4)
# ============================================================================

class TestFallbackRate:
    def test_valid(self):
        m = FallbackRate(value=15.0, status="ok", fallback_events=15, total_interactions=100)
        assert m.fallback_events == 15
        assert m.total_interactions == 100


# ============================================================================
# TopFallbackMessage / TopFallbackMessages (M5)
# ============================================================================

class TestTopFallbackMessage:
    def test_valid(self):
        m = TopFallbackMessage(message="No entiendo", count=42)
        assert m.message == "No entiendo"
        assert m.count == 42


class TestTopFallbackMessages:
    def test_valid(self):
        m = TopFallbackMessages(
            value=3, status="ok",
            messages=[
                TopFallbackMessage(message="msg1", count=10),
                TopFallbackMessage(message="msg2", count=5),
                TopFallbackMessage(message="msg3", count=2),
            ],
        )
        assert len(m.messages) == 3
        assert m.messages[0].message == "msg1"

    def test_empty_messages(self):
        m = TopFallbackMessages(value=0, status="ok", messages=[])
        assert m.messages == []

    def test_default_messages(self):
        m = TopFallbackMessages(value=0, status="ok")
        assert m.messages == []


# ============================================================================
# NocturnalAppointmentRate (M6)
# ============================================================================

class TestNocturnalAppointmentRate:
    def test_valid(self):
        m = NocturnalAppointmentRate(
            value=20.0, status="ok", nocturnal_appointments=10, total_appointments=50,
        )
        assert m.nocturnal_appointments == 10


# ============================================================================
# AutonomousResolutionRate (M7)
# ============================================================================

class TestAutonomousResolutionRate:
    def test_valid(self):
        m = AutonomousResolutionRate(
            value=85.0, status="ok", autonomous_resolutions=85, total_resolutions=100,
        )
        assert m.autonomous_resolutions == 85
        assert m.total_resolutions == 100


# ============================================================================
# CancellationRate (M8)
# ============================================================================

class TestCancellationRate:
    def test_valid(self):
        m = CancellationRate(
            value=12.0, status="ok", cancelled_appointments=12, total_appointments=100,
        )
        assert m.cancelled_appointments == 12


# ============================================================================
# NoShowRate (M9)
# ============================================================================

class TestNoShowRate:
    def test_valid(self):
        m = NoShowRate(value=8.0, status="ok", no_shows=5, total_with_reminder=63)
        assert m.no_shows == 5
        assert m.total_with_reminder == 63


# ============================================================================
# ReminderConfirmationRate (M10)
# ============================================================================

class TestReminderConfirmationRate:
    def test_valid(self):
        m = ReminderConfirmationRate(
            value=65.0, status="ok", confirmations=65, total_reminders=100,
        )
        assert m.confirmations == 65


# ============================================================================
# TopService / TopServices (M11)
# ============================================================================

class TestTopService:
    def test_valid(self):
        s = TopService(service_id=1, service_name="Corte", count=50)
        assert s.service_id == 1
        assert s.service_name == "Corte"
        assert s.count == 50


class TestTopServices:
    def test_valid(self):
        m = TopServices(
            value=2, status="ok",
            services=[
                TopService(service_id=1, service_name="Corte", count=50),
                TopService(service_id=2, service_name="Tinte", count=30),
            ],
        )
        assert len(m.services) == 2

    def test_empty_services(self):
        m = TopServices(value=0, status="ok")
        assert m.services == []


# ============================================================================
# CSATAverage (M12)
# ============================================================================

class TestCSATAverage:
    def test_valid(self):
        m = CSATAverage(
            value=4.2, status="ok",
            average_score=4.2, min_score=3, max_score=5, total_feedbacks=100,
        )
        assert m.average_score == 4.2
        assert m.min_score == 3
        assert m.max_score == 5
        assert m.total_feedbacks == 100

    def test_missing_total_feedbacks_raises(self):
        with pytest.raises(ValidationError):
            CSATAverage(
                value=4.0, status="ok",
                average_score=4.0, min_score=1, max_score=5,
            )  # type: ignore[arg-type]


# ============================================================================
# AllMetrics
# ============================================================================

class TestAllMetrics:
    """Validación del schema agregador AllMetrics."""

    def test_valid_minimal(self):
        """AllMetrics con solo business_id (todas las métricas None)."""
        m = AllMetrics(business_id=1)
        assert m.business_id == 1
        assert m.period == "30d"
        assert m.conversion_rate is None
        assert m.bot_autonomy_rate is None
        assert m.abandonment_rate is None
        assert m.fallback_rate is None
        assert m.top_fallback_messages is None
        assert m.nocturnal_appointment_rate is None
        assert m.autonomous_resolution_rate is None
        assert m.cancellation_rate is None
        assert m.no_show_rate is None
        assert m.reminder_confirmation_rate is None
        assert m.top_services is None
        assert m.csat_average is None

    def test_valid_with_custom_period(self):
        """AllMetrics con período personalizado."""
        m = AllMetrics(business_id=2, period="7d")
        assert m.period == "7d"

    def test_valid_full(self):
        """AllMetrics con todas las métricas pobladas."""
        m = AllMetrics(
            business_id=1,
            period="30d",
            conversion_rate=ConversionRate(value=45.0, status="ok", starts=100, appointments=45),
            bot_autonomy_rate=BotAutonomyRate(value=80.0, status="ok", bot_appointments=36, total_appointments=45),
            abandonment_rate=AbandonmentRate(value=25.0, status="ok", abandoned_sessions=5, total_sessions=20),
            fallback_rate=FallbackRate(value=15.0, status="ok", fallback_events=15, total_interactions=100),
            top_fallback_messages=TopFallbackMessages(value=2, status="ok", messages=[
                TopFallbackMessage(message="msg1", count=10),
                TopFallbackMessage(message="msg2", count=5),
            ]),
            nocturnal_appointment_rate=NocturnalAppointmentRate(value=20.0, status="ok", nocturnal_appointments=9, total_appointments=45),
            autonomous_resolution_rate=AutonomousResolutionRate(value=85.0, status="ok", autonomous_resolutions=85, total_resolutions=100),
            cancellation_rate=CancellationRate(value=12.0, status="ok", cancelled_appointments=5, total_appointments=45),
            no_show_rate=NoShowRate(value=8.0, status="ok", no_shows=5, total_with_reminder=63),
            reminder_confirmation_rate=ReminderConfirmationRate(value=65.0, status="ok", confirmations=65, total_reminders=100),
            top_services=TopServices(value=2, status="ok", services=[
                TopService(service_id=1, service_name="Corte", count=50),
            ]),
            csat_average=CSATAverage(value=4.2, status="ok", average_score=4.2, min_score=3, max_score=5, total_feedbacks=100),
        )
        assert m.conversion_rate.starts == 100  # type: ignore[union-attr]
        assert m.csat_average.average_score == 4.2  # type: ignore[union-attr]
        assert len(m.top_services.services) == 1  # type: ignore[union-attr]

    def test_missing_business_id_raises(self):
        with pytest.raises(ValidationError):
            AllMetrics()  # type: ignore[arg-type]

    def test_model_config_from_attributes(self):
        """Verificar que model_config permite from_attributes=True."""
        assert AllMetrics.model_config.get("from_attributes") is True

    def test_dict_serialization(self):
        """AllMetrics se serializa a dict correctamente."""
        m = AllMetrics(business_id=1)
        d = m.model_dump()
        assert d["business_id"] == 1
        assert d["period"] == "30d"
        assert d["conversion_rate"] is None
        assert d["csat_average"] is None
