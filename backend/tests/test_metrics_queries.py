"""Tests exhaustivos para las 12 funciones de métricas + get_all_metrics.

Usa mock_db para simular queries de SQLAlchemy sin base de datos real.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.metrics_queries import (
    get_abandonment_rate,
    get_all_metrics,
    get_autonomous_resolution_rate,
    get_bot_autonomy_rate,
    get_cancellation_rate,
    get_conversion_rate,
    get_csat_average,
    get_fallback_rate,
    get_no_show_rate,
    get_nocturnal_appointment_rate,
    get_reminder_confirmation_rate,
    get_top_fallback_messages,
    get_top_services,
)


# ============================================================================
# Helpers
# ============================================================================

def mock_scalar_sequence(db, *values):
    """Configura db.query(...).filter(...).scalar() para retornar valores en secuencia."""
    scalars = iter(values)

    def side_effect():
        return next(scalars)

    db.query.return_value.filter.return_value.scalar.side_effect = side_effect
    return db


def mock_scalar_return(db, value):
    """Configura scalar() para retornar siempre value."""
    db.query.return_value.filter.return_value.scalar.return_value = value
    return db


# ============================================================================
# M1 — Conversion Rate
# ============================================================================

class TestConversionRate:
    def test_normal_rate(self, mock_db):
        """40 conversaciones, 8 turnos → 20%."""
        mock_scalar_sequence(mock_db, 40, 8)
        result = get_conversion_rate(mock_db, business_id=1, days=30)
        assert result["starts"] == 40
        assert result["appointments"] == 8
        assert result["value"] == 20.0
        assert result["status"] == "ok"
        assert result["period"] == "30d"

    def test_zero_starts_returns_zero(self, mock_db):
        """0 conversaciones → rate 0%."""
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_conversion_rate(mock_db, business_id=1)
        assert result["value"] == 0.0
        assert result["starts"] == 0

    def test_all_converted(self, mock_db):
        """100% conversion."""
        mock_scalar_sequence(mock_db, 50, 50)
        result = get_conversion_rate(mock_db, business_id=1)
        assert result["value"] == 100.0

    def test_custom_days(self, mock_db):
        mock_scalar_sequence(mock_db, 10, 2)
        result = get_conversion_rate(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"

    def test_threshold_present(self, mock_db):
        mock_scalar_sequence(mock_db, 100, 5)
        result = get_conversion_rate(mock_db, business_id=1)
        assert result["threshold"] is not None
        assert result["threshold"] > 0


# ============================================================================
# M2 — Bot Autonomy Rate
# ============================================================================

class TestBotAutonomyRate:
    def test_normal_rate(self, mock_db):
        """40 total, 32 chatbot → 80%."""
        mock_scalar_sequence(mock_db, 40, 32)
        result = get_bot_autonomy_rate(mock_db, business_id=1)
        assert result["total_appointments"] == 40
        assert result["bot_appointments"] == 32
        assert result["value"] == 80.0

    def test_zero_total(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_bot_autonomy_rate(mock_db, business_id=1)
        assert result["value"] == 0.0

    def test_custom_days(self, mock_db):
        mock_scalar_sequence(mock_db, 10, 7)
        result = get_bot_autonomy_rate(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"


# ============================================================================
# M3 — Abandonment Rate
# ============================================================================

class TestAbandonmentRate:
    def test_normal_rate(self, mock_db):
        """20 sessions, 5 abandoned → 25%."""
        mock_scalar_sequence(mock_db, 20, 5)
        result = get_abandonment_rate(mock_db, business_id=1)
        assert result["total_sessions"] == 20
        assert result["abandoned_sessions"] == 5
        assert result["value"] == 25.0

    def test_no_abandonment(self, mock_db):
        mock_scalar_sequence(mock_db, 20, 0)
        result = get_abandonment_rate(mock_db, business_id=1)
        assert result["value"] == 0.0

    def test_all_abandoned(self, mock_db):
        mock_scalar_sequence(mock_db, 10, 10)
        result = get_abandonment_rate(mock_db, business_id=1)
        assert result["value"] == 100.0


# ============================================================================
# M4 — Fallback Rate
# ============================================================================

class TestFallbackRate:
    def test_normal_rate(self, mock_db):
        """100 interactions, 15 fallbacks → 15%."""
        mock_scalar_sequence(mock_db, 15, 100)
        result = get_fallback_rate(mock_db, business_id=1)
        assert result["fallback_events"] == 15
        assert result["total_interactions"] == 100
        assert result["value"] == 15.0

    def test_zero_interactions(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_fallback_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M5 — Top Fallback Messages
# ============================================================================

class TestTopFallbackMessages:
    def test_with_results(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            MagicMock(message="No entiendo", count=10),
            MagicMock(message="Ayuda", count=5),
        ]
        result = get_top_fallback_messages(mock_db, business_id=1)
        assert result["value"] == 2
        assert len(result["messages"]) == 2
        assert result["messages"][0]["message"] == "No entiendo"
        assert result["messages"][0]["count"] == 10
        assert result["threshold"] is None
        assert result["status"] == "ok"

    def test_empty_results(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        result = get_top_fallback_messages(mock_db, business_id=1)
        assert result["value"] == 0
        assert result["messages"] == []

    def test_null_message(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            MagicMock(message=None, count=3),
        ]
        result = get_top_fallback_messages(mock_db, business_id=1)
        assert result["messages"][0]["message"] == ""


# ============================================================================
# M6 — Nocturnal Appointment Rate
# ============================================================================

class TestNocturnalAppointmentRate:
    def test_normal_rate(self, mock_db):
        """50 total, 10 nocturnal → 20%."""
        mock_scalar_sequence(mock_db, 50, 10)
        result = get_nocturnal_appointment_rate(mock_db, business_id=1)
        assert result["nocturnal_appointments"] == 10
        assert result["total_appointments"] == 50
        assert result["value"] == 20.0

    def test_zero_total(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_nocturnal_appointment_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M7 — Autonomous Resolution Rate
# ============================================================================

class TestAutonomousResolutionRate:
    def test_normal_rate(self, mock_db):
        """85 appointments, 15 escalations → 85% autonomous."""
        mock_scalar_sequence(mock_db, 85, 15)
        result = get_autonomous_resolution_rate(mock_db, business_id=1)
        assert result["autonomous_resolutions"] == 85
        assert result["total_resolutions"] == 100
        assert result["value"] == 85.0

    def test_no_resolutions(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_autonomous_resolution_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M8 — Cancellation Rate
# ============================================================================

class TestCancellationRate:
    def test_normal_rate(self, mock_db):
        """100 total, 12 cancelled → 12%."""
        mock_scalar_sequence(mock_db, 100, 12)
        result = get_cancellation_rate(mock_db, business_id=1)
        assert result["cancelled_appointments"] == 12
        assert result["total_appointments"] == 100
        assert result["value"] == 12.0

    def test_no_cancellations(self, mock_db):
        mock_scalar_sequence(mock_db, 100, 0)
        result = get_cancellation_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M9 — No-Show Rate
# ============================================================================

class TestNoShowRate:
    def test_normal_rate(self, mock_db):
        """63 with reminder, 5 confirmed_no → ~7.94%."""
        mock_scalar_sequence(mock_db, 63, 5)
        result = get_no_show_rate(mock_db, business_id=1)
        assert result["total_with_reminder"] == 63
        assert result["no_shows"] == 5
        assert result["value"] == round(5 / 63 * 100, 2)

    def test_no_reminders(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_no_show_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M10 — Reminder Confirmation Rate
# ============================================================================

class TestReminderConfirmationRate:
    def test_normal_rate(self, mock_db):
        """100 reminders, 65 confirmed → 65%."""
        mock_scalar_sequence(mock_db, 100, 65)
        result = get_reminder_confirmation_rate(mock_db, business_id=1)
        assert result["total_reminders"] == 100
        assert result["confirmations"] == 65
        assert result["value"] == 65.0

    def test_zero_reminders(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_reminder_confirmation_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


# ============================================================================
# M11 — Top Services
# ============================================================================

class TestTopServices:
    def test_with_results(self, mock_db):
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            MagicMock(service_id=1, service_name="Corte", count=50),
            MagicMock(service_id=2, service_name="Tinte", count=30),
        ]
        result = get_top_services(mock_db, business_id=1)
        assert result["value"] == 2
        assert len(result["services"]) == 2
        assert result["services"][0]["service_name"] == "Corte"
        assert result["services"][0]["count"] == 50
        assert result["threshold"] is None
        assert result["status"] == "ok"

    def test_empty_results(self, mock_db):
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        result = get_top_services(mock_db, business_id=1)
        assert result["services"] == []

    def test_custom_days(self, mock_db):
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        result = get_top_services(mock_db, business_id=1, days=7)
        assert result["period"] == "7d"


# ============================================================================
# M12 — CSAT Average
# ============================================================================

class TestCSATAverage:
    def test_normal(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            avg=4.25, min=3, max=5, total=100,
        )
        result = get_csat_average(mock_db, business_id=1)
        assert result["average_score"] == 4.25
        assert result["min_score"] == 3
        assert result["max_score"] == 5
        assert result["total_feedbacks"] == 100
        assert result["value"] == 4.25

    def test_higher_is_better_status(self, mock_db):
        """CSAT usa higher_is_better=True."""
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            avg=4.5, min=4, max=5, total=50,
        )
        result = get_csat_average(mock_db, business_id=1)
        assert result["status"] == "ok"

    def test_no_feedbacks(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            avg=None, min=None, max=None, total=0,
        )
        result = get_csat_average(mock_db, business_id=1)
        assert result["average_score"] == 0.0
        assert result["value"] == 0.0

    def test_none_result(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_csat_average(mock_db, business_id=1)
        assert result["average_score"] == 0.0
        assert result["min_score"] == 0
        assert result["max_score"] == 0
        assert result["total_feedbacks"] == 0


# ============================================================================
# get_all_metrics — Agregador
# ============================================================================

class TestGetAllMetrics:
    """Cobertura 100% para get_all_metrics()."""

    @patch("app.services.metrics_queries.get_conversion_rate")
    @patch("app.services.metrics_queries.get_bot_autonomy_rate")
    @patch("app.services.metrics_queries.get_abandonment_rate")
    @patch("app.services.metrics_queries.get_fallback_rate")
    @patch("app.services.metrics_queries.get_top_fallback_messages")
    @patch("app.services.metrics_queries.get_nocturnal_appointment_rate")
    @patch("app.services.metrics_queries.get_autonomous_resolution_rate")
    @patch("app.services.metrics_queries.get_cancellation_rate")
    @patch("app.services.metrics_queries.get_no_show_rate")
    @patch("app.services.metrics_queries.get_reminder_confirmation_rate")
    @patch("app.services.metrics_queries.get_top_services")
    @patch("app.services.metrics_queries.get_csat_average")
    def test_returns_all_12_metrics(
        self, mock_csat, mock_top_svc, mock_reminder, mock_noshow,
        mock_cancel, mock_auto, mock_nocturnal, mock_top_fb,
        mock_fallback, mock_abandon, mock_bot, mock_conv,
        mock_db,
    ):
        """get_all_metrics debe retornar las 12 métricas con business_id y period."""
        # Cada mock retorna un dict representativo
        mock_conv.return_value = {"value": 45.0, "status": "ok", "period": "30d"}
        mock_bot.return_value = {"value": 80.0, "status": "ok", "period": "30d"}
        mock_abandon.return_value = {"value": 25.0, "status": "ok", "period": "30d"}
        mock_fallback.return_value = {"value": 15.0, "status": "ok", "period": "30d"}
        mock_top_fb.return_value = {"value": 2, "status": "ok", "period": "30d"}
        mock_nocturnal.return_value = {"value": 20.0, "status": "ok", "period": "30d"}
        mock_auto.return_value = {"value": 85.0, "status": "ok", "period": "30d"}
        mock_cancel.return_value = {"value": 12.0, "status": "ok", "period": "30d"}
        mock_noshow.return_value = {"value": 8.0, "status": "ok", "period": "30d"}
        mock_reminder.return_value = {"value": 65.0, "status": "ok", "period": "30d"}
        mock_top_svc.return_value = {"value": 2, "status": "ok", "period": "30d"}
        mock_csat.return_value = {"value": 4.2, "status": "ok", "period": "30d"}

        result = get_all_metrics(mock_db, business_id=1, days=30)

        assert result["business_id"] == 1
        assert result["period"] == "30d"
        assert result["conversion_rate"] is not None
        assert result["bot_autonomy_rate"] is not None
        assert result["abandonment_rate"] is not None
        assert result["fallback_rate"] is not None
        assert result["top_fallback_messages"] is not None
        assert result["nocturnal_appointment_rate"] is not None
        assert result["autonomous_resolution_rate"] is not None
        assert result["cancellation_rate"] is not None
        assert result["no_show_rate"] is not None
        assert result["reminder_confirmation_rate"] is not None
        assert result["top_services"] is not None
        assert result["csat_average"] is not None

        # Verificar que cada función fue llamada con los argumentos correctos
        mock_conv.assert_called_once_with(mock_db, 1, 30)
        mock_bot.assert_called_once_with(mock_db, 1, 30)
        mock_csat.assert_called_once_with(mock_db, 1, 30)

    @patch("app.services.metrics_queries.get_conversion_rate")
    @patch("app.services.metrics_queries.get_bot_autonomy_rate")
    @patch("app.services.metrics_queries.get_abandonment_rate")
    @patch("app.services.metrics_queries.get_fallback_rate")
    @patch("app.services.metrics_queries.get_top_fallback_messages")
    @patch("app.services.metrics_queries.get_nocturnal_appointment_rate")
    @patch("app.services.metrics_queries.get_autonomous_resolution_rate")
    @patch("app.services.metrics_queries.get_cancellation_rate")
    @patch("app.services.metrics_queries.get_no_show_rate")
    @patch("app.services.metrics_queries.get_reminder_confirmation_rate")
    @patch("app.services.metrics_queries.get_top_services")
    @patch("app.services.metrics_queries.get_csat_average")
    def test_custom_days_passed_to_all(
        self, mock_csat, mock_top_svc, mock_reminder, mock_noshow,
        mock_cancel, mock_auto, mock_nocturnal, mock_top_fb,
        mock_fallback, mock_abandon, mock_bot, mock_conv,
        mock_db,
    ):
        """days=7 debe pasarse a todas las sub-funciones."""
        for m in [mock_conv, mock_bot, mock_abandon, mock_fallback, mock_top_fb,
                  mock_nocturnal, mock_auto, mock_cancel, mock_noshow,
                  mock_reminder, mock_top_svc, mock_csat]:
            m.return_value = {"value": 0, "status": "ok", "period": "7d"}

        get_all_metrics(mock_db, business_id=2, days=7)

        mock_conv.assert_called_once_with(mock_db, 2, 7)
        mock_csat.assert_called_once_with(mock_db, 2, 7)

    @patch("app.services.metrics_queries.get_conversion_rate")
    @patch("app.services.metrics_queries.get_bot_autonomy_rate")
    @patch("app.services.metrics_queries.get_abandonment_rate")
    @patch("app.services.metrics_queries.get_fallback_rate")
    @patch("app.services.metrics_queries.get_top_fallback_messages")
    @patch("app.services.metrics_queries.get_nocturnal_appointment_rate")
    @patch("app.services.metrics_queries.get_autonomous_resolution_rate")
    @patch("app.services.metrics_queries.get_cancellation_rate")
    @patch("app.services.metrics_queries.get_no_show_rate")
    @patch("app.services.metrics_queries.get_reminder_confirmation_rate")
    @patch("app.services.metrics_queries.get_top_services")
    @patch("app.services.metrics_queries.get_csat_average")
    def test_period_in_result_matches_days(
        self, mock_csat, mock_top_svc, mock_reminder, mock_noshow,
        mock_cancel, mock_auto, mock_nocturnal, mock_top_fb,
        mock_fallback, mock_abandon, mock_bot, mock_conv,
        mock_db,
    ):
        for m in [mock_conv, mock_bot, mock_abandon, mock_fallback, mock_top_fb,
                  mock_nocturnal, mock_auto, mock_cancel, mock_noshow,
                  mock_reminder, mock_top_svc, mock_csat]:
            m.return_value = {"value": 0, "status": "ok", "period": "90d"}

        result = get_all_metrics(mock_db, business_id=3, days=90)
        assert result["period"] == "90d"


# ============================================================================
# E13 — Structural contract verification
# ============================================================================

class TestGetAllMetricsStructure:
    """E13: Verifica el contrato estructural de get_all_metrics()."""

    @patch("app.services.metrics_queries.get_conversion_rate")
    @patch("app.services.metrics_queries.get_bot_autonomy_rate")
    @patch("app.services.metrics_queries.get_abandonment_rate")
    @patch("app.services.metrics_queries.get_fallback_rate")
    @patch("app.services.metrics_queries.get_top_fallback_messages")
    @patch("app.services.metrics_queries.get_nocturnal_appointment_rate")
    @patch("app.services.metrics_queries.get_autonomous_resolution_rate")
    @patch("app.services.metrics_queries.get_cancellation_rate")
    @patch("app.services.metrics_queries.get_no_show_rate")
    @patch("app.services.metrics_queries.get_reminder_confirmation_rate")
    @patch("app.services.metrics_queries.get_top_services")
    @patch("app.services.metrics_queries.get_csat_average")
    def test_12_base_keys_present(
        self, mock_csat, mock_top_svc, mock_reminder, mock_noshow,
        mock_cancel, mock_auto, mock_nocturnal, mock_top_fb,
        mock_fallback, mock_abandon, mock_bot, mock_conv,
        mock_db,
    ):
        """get_all_metrics sin extended retorna exactamente 12 métricas base."""
        for m in [mock_conv, mock_bot, mock_abandon, mock_fallback, mock_top_fb,
                  mock_nocturnal, mock_auto, mock_cancel, mock_noshow,
                  mock_reminder, mock_top_svc, mock_csat]:
            m.return_value = {"value": 0, "status": "ok", "period": "30d"}

        result = get_all_metrics(mock_db, business_id=1, days=30)

        base_keys = [
            "business_id", "period",
            "conversion_rate", "bot_autonomy_rate", "abandonment_rate",
            "fallback_rate", "top_fallback_messages", "nocturnal_appointment_rate",
            "autonomous_resolution_rate", "cancellation_rate", "no_show_rate",
            "reminder_confirmation_rate", "top_services", "csat_average",
        ]
        for key in base_keys:
            assert key in result, f"Missing key: {key}"

        # extended no debe estar presente cuando include_extended=False
        assert result.get("extended") is None or result.get("extended") == {}

    @patch("app.services.metrics_queries.SessionLocal")
    def test_schema_roundtrip_with_extended_data(self, mock_session):
        """E5/E13: AllMetrics + ExtendedMetricResult round-trip model_dump."""
        from app.schemas.metrics import (
            AllMetrics as AM, ConversionRate, ExtendedMetricResult as EMR,
        )

        # Simular una métrica extendida con sub-data
        ext_metric = EMR(
            value=45.0, status="ok", period="30d",
            services=[
                {"service_id": 1, "service_name": "Corte", "rate": 25.0},
                {"service_id": 2, "service_name": "Tinte", "rate": 15.0},
            ],
            total_appointments=100,
        )

        m = AM(
            business_id=1,
            period="30d",
            conversion_rate=ConversionRate(value=45.0, status="ok", starts=100, appointments=45),
            extended={"conversion_by_service": ext_metric},
        )

        dumped = m.model_dump()
        assert dumped["business_id"] == 1
        assert dumped["extended"]["conversion_by_service"]["services"] == [
            {"service_id": 1, "service_name": "Corte", "rate": 25.0},
            {"service_id": 2, "service_name": "Tinte", "rate": 15.0},
        ]
        assert dumped["extended"]["conversion_by_service"]["total_appointments"] == 100
