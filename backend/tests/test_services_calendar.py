"""Tests para calendar service — CRUD de turnos (appointments)."""

from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.services.calendar import (
    cancel_appointment,
    create_appointment,
    get_appointment,
    get_appointments_by_date,
    get_appointments_by_phone,
    get_appointments_by_week,
    update_appointment_status,
)


class TestCreateAppointment:
    def test_creates_and_returns_appointment(self, mock_db):
        def refresh_side_effect(obj):
            obj.id = 100
        mock_db.refresh.side_effect = refresh_side_effect
        data = {
            "business_id": 1, "service_id": 2,
            "scheduled_date": datetime(2026, 1, 15, 10, 0),
            "user_phone": "5491112345678",
            "user_name": "Cliente Test",
        }

        result = create_appointment(mock_db, data)
        assert result.id == 100
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestGetAppointmentsByDate:
    def test_returns_appointments_for_date(self, mock_db):
        target = date(2026, 1, 15)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1), MagicMock(id=2),
        ]
        result = get_appointments_by_date(mock_db, business_id=1, target_date=target)
        assert len(result) == 2


class TestGetAppointmentsByWeek:
    def test_returns_appointments_for_week(self, mock_db):
        start = date(2026, 1, 12)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1),
        ]
        result = get_appointments_by_week(mock_db, business_id=1, start_date=start)
        assert len(result) == 1


class TestGetAppointment:
    def test_returns_appointment_when_found(self, mock_db):
        expected = MagicMock(id=1)
        mock_db.query.return_value.filter.return_value.first.return_value = expected
        result = get_appointment(mock_db, appointment_id=1, business_id=1)
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_appointment(mock_db, appointment_id=999, business_id=1)
        assert result is None


class TestGetAppointmentsByPhone:
    def test_returns_appointments_for_phone(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1), MagicMock(id=2), MagicMock(id=3),
        ]
        result = get_appointments_by_phone(mock_db, business_id=1, user_phone="5491112345678")
        assert len(result) == 3


class TestCancelAppointment:
    def test_cancels_appointment_with_reason(self, mock_db):
        appointment = MagicMock(id=1, status="scheduled", scheduled_date=datetime(2026, 1, 15, 10, 0))
        mock_db.query.return_value.filter.return_value.first.return_value = appointment

        result = cancel_appointment(mock_db, appointment_id=1, business_id=1, reason="Cliente no puede")
        assert result.status == "cancelled"
        assert result.cancelled_reason == "Cliente no puede"
        assert result.cancellation_scheduled_date is not None
        mock_db.commit.assert_called_once()

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = cancel_appointment(mock_db, appointment_id=999, business_id=1, reason="x")
        assert result is None


class TestUpdateAppointmentStatus:
    def test_updates_status(self, mock_db):
        appointment = MagicMock(id=1, status="scheduled")
        mock_db.query.return_value.filter.return_value.first.return_value = appointment

        result = update_appointment_status(mock_db, appointment_id=1, business_id=1, status="completed")
        assert result.status == "completed"
        mock_db.commit.assert_called_once()

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = update_appointment_status(mock_db, appointment_id=999, business_id=1, status="completed")
        assert result is None
