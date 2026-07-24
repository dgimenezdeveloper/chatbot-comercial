"""Tests exhaustivos para las funciones de utilidad _status y _since de metrics_queries."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.metrics_queries import _status, _since, THRESHOLDS


class TestSince:
    def test_returns_datetime_with_utc_timezone(self):
        result = _since(30)
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_returns_correct_offset_30_days(self):
        now = datetime.now(timezone.utc)
        result = _since(30)
        delta = now - result
        assert timedelta(days=29) <= delta <= timedelta(days=31)


class TestStatusLowerIsBetter:
    def test_critical_when_above_critical(self):
        # conversion_rate tiene higher_is_better=True
        assert _status(0.05, "conversion_rate", higher_is_better=True) == "critical"

    def test_ok_for_nocturnal_rate(self):
        # nocturnal_appointment_rate: warning=0.10, critical=0.30 (lower is better)
        assert _status(0.05, "nocturnal_appointment_rate") == "ok"


class TestStatusEdgeCases:
    def test_boundary_values(self):
        assert _status(0.20, "conversion_rate", higher_is_better=True) == "ok"
        assert _status(0.15, "conversion_rate", higher_is_better=True) == "warning"