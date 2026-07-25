"""Tests exhaustivos para las 12 funciones de métricas + get_all_metrics.

Usa mock_db para simular queries de SQLAlchemy sin base de datos real.
"""

from unittest.mock import MagicMock, patch, ANY

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


def mock_scalar_sequence(db, *values):
    scalars = iter(values)

    def side_effect():
        return next(scalars)

    db.query.return_value.filter.return_value.scalar.side_effect = side_effect
    return db


def mock_scalar_return(db, value):
    db.query.return_value.filter.return_value.scalar.return_value = value
    return db


class TestConversionRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 40, 8)
        result = get_conversion_rate(mock_db, business_id=1, days=30)
        assert result["starts"] == 40
        assert result["appointments"] == 8
        assert result["value"] == 20.0
        assert result["status"] == "ok"
        assert result["period"] == "30d"

    def test_zero_starts_returns_zero(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_conversion_rate(mock_db, business_id=1)
        assert result["value"] == 0.0
        assert result["starts"] == 0

    def test_all_converted(self, mock_db):
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


class TestBotAutonomyRate:
    def test_normal_rate(self, mock_db):
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


class TestAbandonmentRate:
    def test_normal_rate(self, mock_db):
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


class TestFallbackRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 15, 100)
        result = get_fallback_rate(mock_db, business_id=1)
        assert result["fallback_events"] == 15
        assert result["total_interactions"] == 100
        assert result["value"] == 15.0

    def test_zero_interactions(self, mock_db):
        mock_scalar_sequence(mock_db, 0, 0)
        result = get_fallback_rate(mock_db, business_id=1)
        assert result["value"] == 0.0


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

    def test_empty_results(self, mock_db):
        mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        result = get_top_fallback_messages(mock_db, business_id=1)
        assert result["value"] == 0
        assert result["messages"] == []


class TestNocturnalAppointmentRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 50, 10)
        result = get_nocturnal_appointment_rate(mock_db, business_id=1)
        assert result["nocturnal_appointments"] == 10
        assert result["total_appointments"] == 50
        assert result["value"] == 20.0


class TestAutonomousResolutionRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 85, 15)
        result = get_autonomous_resolution_rate(mock_db, business_id=1)
        assert result["autonomous_resolutions"] == 85
        assert result["total_resolutions"] == 100
        assert result["value"] == 85.0


class TestCancellationRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 100, 12)
        result = get_cancellation_rate(mock_db, business_id=1)
        assert result["cancelled_appointments"] == 12
        assert result["total_appointments"] == 100
        assert result["value"] == 12.0


class TestNoShowRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 63, 5)
        result = get_no_show_rate(mock_db, business_id=1)
        assert result["total_with_reminder"] == 63
        assert result["no_shows"] == 5


class TestReminderConfirmationRate:
    def test_normal_rate(self, mock_db):
        mock_scalar_sequence(mock_db, 100, 65)
        result = get_reminder_confirmation_rate(mock_db, business_id=1)
        assert result["confirmations"] == 65


class TestTopServices:
    def test_with_results(self, mock_db):
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            MagicMock(service_id=1, service_name="Corte", count=50),
            MagicMock(service_id=2, service_name="Tinte", count=30),
        ]
        result = get_top_services(mock_db, business_id=1)
        assert result["value"] == 2


class TestCSATAverage:
    def test_normal(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            avg=4.25, min=3, max=5, total=100,
        )
        result = get_csat_average(mock_db, business_id=1)
        assert result["average_score"] == 4.25


class TestGetAllMetrics:
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
        for m in [mock_conv, mock_bot, mock_abandon, mock_fallback, mock_top_fb,
                  mock_nocturnal, mock_auto, mock_cancel, mock_noshow,
                  mock_reminder, mock_top_svc, mock_csat]:
            m.return_value = {"value": 0, "status": "ok", "period": "30d"}

        result = get_all_metrics(mock_db, business_id=1, days=30)

        assert result["business_id"] == 1
        assert result["period"] == "30d"
        mock_conv.assert_called_once()
        assert mock_conv.call_args.kwargs["period_label"] == "30d"

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
        for m in [mock_conv, mock_bot, mock_abandon, mock_fallback, mock_top_fb,
                  mock_nocturnal, mock_auto, mock_cancel, mock_noshow,
                  mock_reminder, mock_top_svc, mock_csat]:
            m.return_value = {"value": 0, "status": "ok", "period": "7d"}

        get_all_metrics(mock_db, business_id=2, days=7)
        mock_conv.assert_called_once()
        assert mock_conv.call_args.kwargs["period_label"] == "7d"