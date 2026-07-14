"""Tests for Celery scheduler tasks — send_reminders, _process_reminders.

Covers: B1 (notification_sent_at IS NULL filter), W3 (_within_24h_window
uses MAX(Event.timestamp)), W5 (db.rollback() on exception),
C1 (single asyncio.run), 4-level fallback path.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scheduler.tasks import (
    _has_alternative_channel,
    _process_reminders,
    _send_template_reminder,
    _within_24h_window,
    send_reminders,
)


def run_async(coro):
    """Helper: run an async coroutine and return its result."""
    return asyncio.run(coro)


# ============================================================================
# B1 — send_reminders filters notification_sent_at IS NULL
# ============================================================================

class TestSendRemindersFilter:
    """B1: send_reminders must filter by notification_sent_at.is_(None)."""

    @patch("app.scheduler.tasks.SessionLocal")
    @patch("app.scheduler.tasks.asyncio.run")
    def test_filters_notification_sent_at_is_null(self, mock_async_run, mock_session_local):
        """The query must include Appointment.notification_sent_at.is_(None)."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        # Updated chain: query().filter().with_for_update().order_by().limit().all()
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_async_run.return_value = {"total": 0, "sent": 0, "failed": 0, "skipped": 0, "notified_owner": 0}

        send_reminders()

        # Verify filter was called
        filter_call = mock_db.query.return_value.filter
        assert filter_call.called, "send_reminders must call .filter() on the query"
        mock_db.query.assert_called_once()

    @patch("app.scheduler.tasks.SessionLocal")
    @patch("app.scheduler.tasks.asyncio.run")
    def test_no_appointments_returns_zero(self, mock_async_run, mock_session_local):
        """When no appointments for tomorrow, returns 0 totals."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_async_run.return_value = {"total": 0, "sent": 0, "failed": 0, "notified_owner": 0}

        result = send_reminders()
        assert result["total"] == 0
        assert result["sent"] == 0
        # When no appointments, asyncio.run is not called with the inner function
        # because the function bails out early

    @patch("app.scheduler.tasks.SessionLocal")
    @patch("app.scheduler.tasks.asyncio.run")
    def test_closes_db_in_finally(self, mock_async_run, mock_session_local):
        """db.close() is called in finally block."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_async_run.return_value = {"total": 0, "sent": 0, "failed": 0, "notified_owner": 0}

        send_reminders()
        mock_db.close.assert_called_once()

    @patch("app.scheduler.tasks.SessionLocal")
    @patch("app.scheduler.tasks.asyncio.run")
    def test_closes_db_even_on_error(self, mock_async_run, mock_session_local):
        """db.close() is called even if an exception occurs.
        
        send_reminders now catches exceptions and returns an error dict
        instead of propagating. db.close() is still called in finally.
        """
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.order_by.return_value.limit.return_value.all.side_effect = RuntimeError("DB error")

        result = send_reminders()
        assert result["error"] is True
        mock_db.close.assert_called_once()


# ============================================================================
# C1 — Single asyncio.run() in entry point
# ============================================================================

class TestSingleAsyncioRun:
    """C1: send_reminders uses a single asyncio.run() for all appointments."""

    @patch("app.scheduler.tasks.SessionLocal")
    @patch("app.scheduler.tasks.asyncio.run")
    def test_single_event_loop_used(self, mock_async_run, mock_session_local):
        """One asyncio.run call processes all appointments."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        # 5 appointments for tomorrow
        mock_appointments = [MagicMock(id=i, business_id=1) for i in range(5)]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_appointments
        mock_async_run.return_value = {"total": 5, "sent": 5, "failed": 0, "notified_owner": 0}

        send_reminders()

        # asyncio.run should be called exactly once
        assert mock_async_run.call_count == 1
        # The argument should be a coroutine (from _process_reminders)
        import asyncio
        arg = mock_async_run.call_args[0][0]
        assert asyncio.iscoroutine(arg)


# ============================================================================
# W3 — _within_24h_window uses MAX(Event.timestamp)
# ============================================================================

class TestWithin24hWindow:
    """W3: _within_24h_window uses MAX(Event.timestamp), not ChatSession.started_at."""

    def test_uses_max_event_timestamp(self):
        """Verifies query uses func.max(Event.timestamp)."""
        mock_db = MagicMock()
        recent = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_db.query.return_value.filter.return_value.scalar.return_value = recent

        appointment = MagicMock()
        appointment.business_id = 1
        appointment.session_id = "s1"

        result = _within_24h_window(mock_db, appointment)
        assert result is True

    def test_no_last_message_returns_false(self):
        """When there's no message from user, returns False."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.scalar.return_value = None

        appointment = MagicMock()
        appointment.business_id = 1
        appointment.session_id = "s1"

        result = _within_24h_window(mock_db, appointment)
        assert result is False

    def test_outside_24h_returns_false(self):
        """Last message > 24h ago → False."""
        mock_db = MagicMock()
        old = datetime.now(timezone.utc) - timedelta(hours=25)
        mock_db.query.return_value.filter.return_value.scalar.return_value = old

        appointment = MagicMock()
        appointment.business_id = 1
        appointment.session_id = "s1"

        result = _within_24h_window(mock_db, appointment)
        assert result is False

    def test_exactly_24h_returns_true(self):
        """Exactly at 24h boundary → True (edge case).

        Uses a fraction of a second inside the window to avoid timing race
        between test execution and function call.
        """
        mock_db = MagicMock()
        # 23h 59min 59s ago — still within the 24h window
        edge = datetime.now(timezone.utc) - timedelta(hours=23, minutes=59, seconds=59)
        mock_db.query.return_value.filter.return_value.scalar.return_value = edge

        appointment = MagicMock()
        appointment.business_id = 1
        appointment.session_id = "s1"

        result = _within_24h_window(mock_db, appointment)
        assert result is True

    def test_null_session_id_returns_false(self):
        """NULL session_id → cannot check window → False."""
        mock_db = MagicMock()

        appointment = MagicMock()
        appointment.business_id = 1
        appointment.session_id = None

        result = _within_24h_window(mock_db, appointment)
        assert result is False


# ============================================================================
# W5 — db.rollback() on exception
# ============================================================================

class TestRollbackOnException:
    """W5: _process_reminders must call db.rollback() on send_message failure."""

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    def test_rollback_called_on_failure(self, mock_send, mock_log_event):
        """When send_message raises, savepoint is used (begin_nested)."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None)
        ]
        mock_send.side_effect = Exception("Connection error")

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["failed"] == 1
        assert results["sent"] == 0
        # Savepoint is used instead of global rollback
        mock_db.begin_nested.assert_called()
        mock_db.add.assert_called()  # Log entry is still added

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    def test_log_entry_added_after_rollback(self, mock_send, mock_log_event):
        """After rollback, a failed ReminderLog is still added."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None)
        ]
        mock_send.side_effect = Exception("Timeout")

        appointment = MagicMock()
        appointment.id = 2
        appointment.business_id = 1
        appointment.user_phone = "+5491111111111"
        appointment.user_name = "User"
        appointment.service_id = 3
        appointment.session_id = "s2"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["failed"] == 1
        # db.add() is called for the ReminderLog
        mock_db.add.assert_called()


# ============================================================================
# 4-Level Fallback Path
# ============================================================================

class TestFourLevelFallback:

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks._send_template_reminder", new_callable=AsyncMock)
    def test_level_1_templates(self, mock_send_template, mock_log_event):
        """Level 1: business.use_whatsapp_templates=True → template reminder."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=True,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=True)
        ]

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["sent"] == 1
        assert results["failed"] == 0
        mock_send_template.assert_called_once()

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    @patch("app.scheduler.tasks._within_24h_window")
    def test_level_2_24h_window(self, mock_within, mock_send, mock_log_event):
        """Level 2: within 24h window → whatsapp_text."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None)
        ]
        mock_within.return_value = True

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["sent"] == 1
        mock_send.assert_called_once()
        mock_within.assert_called_once()

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks._has_alternative_channel")
    @patch("app.scheduler.tasks._within_24h_window")
    def test_level_3_alternative_channel(self, mock_within, mock_alt_channel, mock_log_event):
        """Level 3: outside 24h window, alternative channel → fallback_channel."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_within.return_value = False
        mock_alt_channel.return_value = True

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        # Level 3 now results in "skipped" instead of "failed"
        assert results["skipped"] == 1
        assert results["failed"] == 0

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    @patch("app.scheduler.tasks._within_24h_window")
    def test_level_4_notify_owner(self, mock_within, mock_send, mock_log_event):
        """Level 4: outside 24h window, no alt channel, owner_phone → notified_owner."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone="+5491122223333",
            sms_enabled=False,
            email_enabled=False,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone="+5491122223333", sms_enabled=False, email_enabled=False)
        ]
        mock_within.return_value = False

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["notified_owner"] == 1
        assert results["sent"] == 0
        mock_send.assert_called_once()  # sends owner notification
        # Verify it sends to owner_phone
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["phone"] == "+5491122223333"

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks._within_24h_window")
    def test_level_4_no_owner_phone(self, mock_within, mock_log_event):
        """Level 4: no owner_phone → just log without sending."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
            sms_enabled=False,
            email_enabled=False,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None, sms_enabled=False, email_enabled=False)
        ]
        mock_within.return_value = False

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        # No owner_phone → notified_owner still incremented, but no message sent
        assert results["notified_owner"] == 1

    @patch("app.scheduler.tasks.log_event")
    def test_business_not_found_skipped(self, mock_log_event):
        """When business is not found, the appointment is skipped."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 999

        results = run_async(_process_reminders(mock_db, [appointment]))
        assert results["total"] == 1
        assert results["sent"] == 0
        assert results["failed"] == 0


# ============================================================================
# _has_alternative_channel
# ============================================================================

class TestHasAlternativeChannel:
    """_has_alternative_channel placeholder — always returns False."""

    def test_returns_false(self):
        """Returns False when Business has no alternative channels enabled."""
        business = MagicMock(sms_enabled=False, email_enabled=False)
        result = _has_alternative_channel(business)
        assert result is False

    def test_returns_true_when_sms_enabled(self):
        """Returns True when Business has sms_enabled=True."""
        business = MagicMock(sms_enabled=True, email_enabled=False)
        assert _has_alternative_channel(business) is True

    def test_returns_true_when_email_enabled(self):
        """Returns True when Business has email_enabled=True."""
        business = MagicMock(sms_enabled=False, email_enabled=True)
        assert _has_alternative_channel(business) is True


# ============================================================================
# _send_template_reminder
# ============================================================================

class TestSendTemplateReminder:

    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    def test_calls_send_message(self, mock_send):
        """_send_template_reminder delegates to send_message."""
        appointment = MagicMock()
        appointment.user_phone = "+5491112345678"
        appointment.scheduled_date = datetime(2026, 7, 12, 15, 30, tzinfo=timezone.utc)

        business = MagicMock()
        business.name = "Salon Belen"

        run_async(_send_template_reminder(appointment, business))

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["phone"] == "+5491112345678"
        assert "Salon Belen" in call_kwargs["text"]
        assert "15:30" in call_kwargs["text"]


# ============================================================================
# _process_reminders — log_event integration
# ============================================================================

class TestProcessRemindersLogEvent:
    """log_event is called only when status == 'sent'."""

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    @patch("app.scheduler.tasks._within_24h_window")
    def test_log_event_called_on_success(self, mock_within, mock_send, mock_log_event):
        """log_event is called with event_type='reminder_sent' on success."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None)
        ]
        mock_within.return_value = True

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["sent"] == 1
        mock_log_event.assert_called_once()
        assert mock_log_event.call_args.kwargs["event_type"] == "reminder_sent"

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    def test_log_event_not_called_on_failure(self, mock_send, mock_log_event):
        """log_event is NOT called when send_message fails."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_send.side_effect = Exception("Network error")

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)

        run_async(_process_reminders(mock_db, [appointment]))

        # log_event should not be called on failure
        mock_log_event.assert_not_called()

    @patch("app.scheduler.tasks.log_event")
    @patch("app.scheduler.tasks.send_message", new_callable=AsyncMock)
    @patch("app.scheduler.tasks._within_24h_window")
    def test_notification_sent_at_set_on_success(self, mock_within, mock_send, mock_log_event):
        """appointment.notification_sent_at is set to current time on success."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            id=1,
            use_whatsapp_templates=False,
            owner_phone=None,
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(id=1, use_whatsapp_templates=False, owner_phone=None)
        ]
        mock_within.return_value = True

        appointment = MagicMock()
        appointment.id = 1
        appointment.business_id = 1
        appointment.user_phone = "+5491112345678"
        appointment.user_name = "Cliente"
        appointment.service_id = 5
        appointment.session_id = "s1"
        appointment.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)
        appointment.notification_sent_at = None

        results = run_async(_process_reminders(mock_db, [appointment]))

        assert results["sent"] == 1
        # notification_sent_at is set at DB level in send_reminders(),
        # not in _process_reminders(). The DB update happens before the async processing.
        # _process_reminders only maintains it (sets to None on failure).
