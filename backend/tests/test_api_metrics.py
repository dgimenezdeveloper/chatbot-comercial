"""Tests para el endpoint GET /api/v1/admin/metrics."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.admin.metrics import router as metrics_router


def _make_app() -> FastAPI:
    """Crea una app FastAPI standalone solo con el router de métricas."""
    app = FastAPI()
    app.include_router(metrics_router, prefix="/api/v1/admin/metrics")
    return app


class TestGetMetricsEndpoint:
    """Tests de integración para el endpoint de métricas."""

    @pytest.fixture
    def client(self):
        return TestClient(_make_app())

    @patch("app.api.v1.admin.metrics.SessionLocal")
    @patch("app.api.v1.admin.metrics.get_all_metrics")
    def test_returns_200_with_default_params(self, mock_get_all, mock_session, client):
        """GET /api/v1/admin/metrics con params default → 200."""
        mock_session.return_value = MagicMock()
        mock_get_all.return_value = {
            "business_id": 1,
            "period": "30d",
            "conversion_rate": {"value": 45.0, "status": "ok", "period": "30d"},
            "bot_autonomy_rate": {"value": 80.0, "status": "ok", "period": "30d"},
            "abandonment_rate": {"value": 25.0, "status": "ok", "period": "30d"},
            "fallback_rate": {"value": 15.0, "status": "ok", "period": "30d"},
            "top_fallback_messages": {"value": 2, "status": "ok", "period": "30d", "messages": []},
            "nocturnal_appointment_rate": {"value": 20.0, "status": "ok", "period": "30d"},
            "autonomous_resolution_rate": {"value": 85.0, "status": "ok", "period": "30d"},
            "cancellation_rate": {"value": 12.0, "status": "ok", "period": "30d"},
            "no_show_rate": {"value": 8.0, "status": "ok", "period": "30d"},
            "reminder_confirmation_rate": {"value": 65.0, "status": "ok", "period": "30d"},
            "top_services": {"value": 2, "status": "ok", "period": "30d", "services": []},
            "csat_average": {"value": 4.2, "status": "ok", "period": "30d"},
        }

        response = client.get("/api/v1/admin/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["business_id"] == 1
        assert data["period"] == "30d"
        assert data["conversion_rate"]["value"] == 45.0

    @patch("app.api.v1.admin.metrics.SessionLocal")
    @patch("app.api.v1.admin.metrics.get_all_metrics")
    def test_custom_days_parameter(self, mock_get_all, mock_session, client):
        """GET /api/v1/admin/metrics?days=7 → pasa days=7."""
        mock_session.return_value = MagicMock()
        mock_get_all.return_value = {
            "business_id": 2, "period": "7d",
            "conversion_rate": {"value": 0, "status": "ok", "period": "7d"},
            "bot_autonomy_rate": {"value": 0, "status": "ok", "period": "7d"},
            "abandonment_rate": {"value": 0, "status": "ok", "period": "7d"},
            "fallback_rate": {"value": 0, "status": "ok", "period": "7d"},
            "top_fallback_messages": {"value": 0, "status": "ok", "period": "7d", "messages": []},
            "nocturnal_appointment_rate": {"value": 0, "status": "ok", "period": "7d"},
            "autonomous_resolution_rate": {"value": 0, "status": "ok", "period": "7d"},
            "cancellation_rate": {"value": 0, "status": "ok", "period": "7d"},
            "no_show_rate": {"value": 0, "status": "ok", "period": "7d"},
            "reminder_confirmation_rate": {"value": 0, "status": "ok", "period": "7d"},
            "top_services": {"value": 0, "status": "ok", "period": "7d", "services": []},
            "csat_average": {"value": 0, "status": "ok", "period": "7d"},
        }

        response = client.get("/api/v1/admin/metrics?days=7&business_id=2")
        assert response.status_code == 200
        mock_get_all.assert_called_once()
        # Verificar que days=7 y business_id=2 se pasaron
        call_kwargs = mock_get_all.call_args
        assert call_kwargs[1]["days"] == 7
        assert call_kwargs[1]["business_id"] == 2

    @patch("app.api.v1.admin.metrics.SessionLocal")
    @patch("app.api.v1.admin.metrics.get_all_metrics")
    def test_minimum_days_is_1(self, mock_get_all, mock_session, client):
        """GET /api/v1/admin/metrics?days=1 → 200."""
        mock_session.return_value = MagicMock()
        mock_get_all.return_value = {
            "business_id": 1, "period": "1d",
            "conversion_rate": None, "bot_autonomy_rate": None,
            "abandonment_rate": None, "fallback_rate": None,
            "top_fallback_messages": None, "nocturnal_appointment_rate": None,
            "autonomous_resolution_rate": None, "cancellation_rate": None,
            "no_show_rate": None, "reminder_confirmation_rate": None,
            "top_services": None, "csat_average": None,
        }

        response = client.get("/api/v1/admin/metrics?days=1")
        assert response.status_code == 200

    @patch("app.api.v1.admin.metrics.SessionLocal")
    @patch("app.api.v1.admin.metrics.get_all_metrics")
    def test_maximum_days_is_365(self, mock_get_all, mock_session, client):
        """GET /api/v1/admin/metrics?days=365 → 200."""
        mock_session.return_value = MagicMock()
        mock_get_all.return_value = {
            "business_id": 1, "period": "365d",
            "conversion_rate": None, "bot_autonomy_rate": None,
            "abandonment_rate": None, "fallback_rate": None,
            "top_fallback_messages": None, "nocturnal_appointment_rate": None,
            "autonomous_resolution_rate": None, "cancellation_rate": None,
            "no_show_rate": None, "reminder_confirmation_rate": None,
            "top_services": None, "csat_average": None,
        }

        response = client.get("/api/v1/admin/metrics?days=365")
        assert response.status_code == 200

    def test_invalid_days_zero_rejected(self, client):
        """days=0 → 422 (ge=1)."""
        response = client.get("/api/v1/admin/metrics?days=0")
        assert response.status_code == 422

    def test_invalid_days_negative_rejected(self, client):
        """days=-1 → 422."""
        response = client.get("/api/v1/admin/metrics?days=-1")
        assert response.status_code == 422

    def test_invalid_days_exceeds_max_rejected(self, client):
        """days=366 → 422 (le=365)."""
        response = client.get("/api/v1/admin/metrics?days=366")
        assert response.status_code == 422

    def test_invalid_business_id_zero_rejected(self, client):
        """business_id=0 → 422 (ge=1)."""
        response = client.get("/api/v1/admin/metrics?business_id=0")
        assert response.status_code == 422

    def test_closes_db_session_after_request(self, client):
        """Verifica que la sesión de DB se cierra siempre."""
        with patch("app.api.v1.admin.metrics.SessionLocal") as mock_session, \
             patch("app.api.v1.admin.metrics.get_all_metrics") as mock_get_all:
            mock_db = MagicMock()
            mock_session.return_value = mock_db
            mock_get_all.return_value = {
                "business_id": 1, "period": "30d",
                "conversion_rate": None, "bot_autonomy_rate": None,
                "abandonment_rate": None, "fallback_rate": None,
                "top_fallback_messages": None, "nocturnal_appointment_rate": None,
                "autonomous_resolution_rate": None, "cancellation_rate": None,
                "no_show_rate": None, "reminder_confirmation_rate": None,
                "top_services": None, "csat_average": None,
            }

            response = client.get("/api/v1/admin/metrics")
            assert response.status_code == 200
            mock_db.close.assert_called_once()

    @patch("app.api.v1.admin.metrics.SessionLocal")
    @patch("app.api.v1.admin.metrics.get_all_metrics")
    def test_response_matches_all_metrics_schema(self, mock_get_all, mock_session, client):
        """La respuesta debe ser serializable como AllMetrics."""
        mock_session.return_value = MagicMock()
        mock_get_all.return_value = {
            "business_id": 1,
            "period": "30d",
            "conversion_rate": {
                "value": 45.0, "threshold": 20.0, "status": "ok", "period": "30d",
                "starts": 100, "appointments": 45,
            },
            "bot_autonomy_rate": {
                "value": 80.0, "threshold": 40.0, "status": "ok", "period": "30d",
                "bot_appointments": 36, "total_appointments": 45,
            },
            "abandonment_rate": {
                "value": 25.0, "threshold": 30.0, "status": "ok", "period": "30d",
                "abandoned_sessions": 5, "total_sessions": 20,
            },
            "fallback_rate": {
                "value": 15.0, "threshold": 15.0, "status": "ok", "period": "30d",
                "fallback_events": 15, "total_interactions": 100,
            },
            "top_fallback_messages": {
                "value": 2, "threshold": None, "status": "ok", "period": "30d",
                "messages": [{"message": "msg1", "count": 10}],
            },
            "nocturnal_appointment_rate": {
                "value": 20.0, "threshold": 30.0, "status": "ok", "period": "30d",
                "nocturnal_appointments": 9, "total_appointments": 45,
            },
            "autonomous_resolution_rate": {
                "value": 85.0, "threshold": 70.0, "status": "ok", "period": "30d",
                "autonomous_resolutions": 85, "total_resolutions": 100,
            },
            "cancellation_rate": {
                "value": 12.0, "threshold": 15.0, "status": "ok", "period": "30d",
                "cancelled_appointments": 5, "total_appointments": 45,
            },
            "no_show_rate": {
                "value": 8.0, "threshold": 10.0, "status": "ok", "period": "30d",
                "no_shows": 5, "total_with_reminder": 63,
            },
            "reminder_confirmation_rate": {
                "value": 65.0, "threshold": 60.0, "status": "ok", "period": "30d",
                "confirmations": 65, "total_reminders": 100,
            },
            "top_services": {
                "value": 2, "threshold": None, "status": "ok", "period": "30d",
                "services": [
                    {"service_id": 1, "service_name": "Corte", "count": 50},
                    {"service_id": 2, "service_name": "Tinte", "count": 30},
                ],
            },
            "csat_average": {
                "value": 4.2, "threshold": 4.0, "status": "ok", "period": "30d",
                "average_score": 4.2, "min_score": 3, "max_score": 5, "total_feedbacks": 100,
            },
        }

        response = client.get("/api/v1/admin/metrics")
        assert response.status_code == 200
        data = response.json()

        # Verificar que el schema AllMetrics puede validar la respuesta
        from app.schemas.metrics import AllMetrics
        validated = AllMetrics(**data)
        assert validated.business_id == 1
        assert validated.conversion_rate.starts == 100  # type: ignore[union-attr]
        assert validated.csat_average.average_score == 4.2  # type: ignore[union-attr]
