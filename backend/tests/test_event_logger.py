"""Tests para log_event() — fire-and-forget event logging."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.models.events import Event
from app.services.event_logger import log_event


class TestLogEvent:
    """Cobertura 100% para el patrón fire-and-forget de log_event()."""

    @patch("app.services.event_logger.SessionLocal")
    def test_creates_and_returns_event(self, mock_session_local):
        """Happy path: crea el evento, commitea, y lo retorna."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        result = log_event(
            session_id="wa-session-123",
            business_id=1,
            event_type="conversation_started",
            payload={"key": "value"},
            user_id=42,
            channel="whatsapp",
        )

        # Verificar que se agregó un Event
        mock_db.add.assert_called_once()
        added_event = mock_db.add.call_args[0][0]
        assert isinstance(added_event, Event)
        assert added_event.session_id == "wa-session-123"
        assert added_event.business_id == 1
        assert added_event.event_type == "conversation_started"
        assert added_event.payload_json == {"key": "value"}
        assert added_event.user_id == 42
        assert added_event.channel == "whatsapp"

        # Verificar commit + refresh
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Debe retornar el evento creado
        assert result is not None

        # Debe cerrar la sesión
        mock_db.close.assert_called_once()

    @patch("app.services.event_logger.SessionLocal")
    def test_returns_none_on_exception(self, mock_session_local):
        """Si hay una excepción, retorna None sin propagar."""
        mock_db = MagicMock()
        mock_db.add.side_effect = RuntimeError("DB down")
        mock_session_local.return_value = mock_db

        # No debe propagar la excepción
        result = log_event(
            session_id="wa-session-123",
            business_id=1,
            event_type="test",
        )

        assert result is None
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.services.event_logger.SessionLocal")
    def test_rollback_on_commit_failure(self, mock_session_local):
        """Si commit falla, hace rollback y retorna None."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = RuntimeError("commit failed")
        mock_session_local.return_value = mock_db

        result = log_event(
            session_id="wa-session-123",
            business_id=1,
            event_type="test",
        )

        assert result is None
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.services.event_logger.SessionLocal")
    def test_default_channel(self, mock_session_local):
        """Si no se especifica channel, usa 'whatsapp'."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        log_event(session_id="s1", business_id=1, event_type="test")

        added_event = mock_db.add.call_args[0][0]
        assert added_event.channel == "whatsapp"

    @patch("app.services.event_logger.SessionLocal")
    def test_none_payload(self, mock_session_local):
        """payload=None debe ser aceptado."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        log_event(session_id="s1", business_id=1, event_type="test", payload=None)

        added_event = mock_db.add.call_args[0][0]
        assert added_event.payload_json is None

    @patch("app.services.event_logger.SessionLocal")
    def test_none_user_id(self, mock_session_local):
        """user_id=None debe ser aceptado."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        log_event(session_id="s1", business_id=1, event_type="test")

        added_event = mock_db.add.call_args[0][0]
        assert added_event.user_id is None

    @patch("app.services.event_logger.SessionLocal")
    def test_closes_db_even_on_success(self, mock_session_local):
        """La sesión se cierra siempre (finally)."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        log_event(session_id="s1", business_id=1, event_type="test")

        mock_db.close.assert_called_once()

    @patch("app.services.event_logger.SessionLocal")
    def test_closes_db_even_on_exception(self, mock_session_local):
        """La sesión se cierra incluso cuando hay excepción."""
        mock_db = MagicMock()
        mock_db.add.side_effect = RuntimeError("fail")
        mock_session_local.return_value = mock_db

        log_event(session_id="s1", business_id=1, event_type="test")

        mock_db.close.assert_called_once()

    @patch("app.services.event_logger.SessionLocal")
    def test_refresh_returns_committed_event(self, mock_session_local):
        """El evento retornado es el que se refrescó post-commit."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        result = log_event(session_id="s1", business_id=1, event_type="test")

        mock_db.refresh.assert_called_once_with(result)
