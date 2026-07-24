"""Tests para negocio service — orquestación del chatbot."""

from datetime import date, datetime
import zoneinfo
from unittest.mock import MagicMock, patch

import pytest

from app.services.negocio import (
    get_active_services,
    get_available_slots,
    get_business_by_phone,
    get_business_by_slug,
    get_business_timezone,
    get_or_create_user,
)


class TestGetBusinessBySlug:
    def test_returns_business_when_found(self, mock_db):
        expected = MagicMock(id=1, name="Salon Test", slug="salon-test")
        mock_db.query.return_value.filter.return_value.first.return_value = expected

        result = get_business_by_slug(mock_db, slug="salon-test")
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_business_by_slug(mock_db, slug="no-existe")
        assert result is None


class TestGetBusinessByPhone:
    def test_returns_business_when_found(self, mock_db):
        expected = MagicMock(id=1, whatsapp_phone_id="12345")
        mock_db.query.return_value.filter.return_value.first.return_value = expected

        result = get_business_by_phone(mock_db, phone_id="12345")
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_business_by_phone(mock_db, phone_id="99999")
        assert result is None


class TestGetOrCreateUser:
    def test_returns_existing_user(self, mock_db):
        existing = MagicMock(id=42, phone="5491112345678", name="Juan", role="guest")
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        result = get_or_create_user(mock_db, phone="5491112345678", business_id=1)
        assert result is existing
        mock_db.add.assert_not_called()

    def test_creates_new_user_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def refresh_side_effect(obj):
            obj.id = 99
        mock_db.refresh.side_effect = refresh_side_effect

        result = get_or_create_user(mock_db, phone="5491112345678", business_id=1, name="Maria")
        assert result.id == 99
        assert result.phone == "5491112345678"
        assert result.role == "guest"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_creates_user_with_default_name(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def refresh_side_effect(obj):
            obj.id = 100
        mock_db.refresh.side_effect = refresh_side_effect

        result = get_or_create_user(mock_db, phone="5491112345678", business_id=1)
        assert result.name == "Cliente 5678"


class TestGetActiveServices:
    def test_returns_active_services(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, name="Corte"),
            MagicMock(id=2, name="Tinte"),
        ]
        result = get_active_services(mock_db, business_id=1)
        assert len(result) == 2

    def test_returns_empty_list_when_no_services(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = get_active_services(mock_db, business_id=1)
        assert result == []


class TestGetAvailableSlots:
    @patch("app.services.negocio.get_freebusy", return_value=[])
    def test_returns_slots_for_service_with_no_occupancy(self, mock_gcal, mock_db):
        """Sin turnos ocupados, debe devolver todos los slots del día."""
        service = MagicMock(id=1, duration_minutes=60)
        business = MagicMock(id=1, timezone="America/Argentina/Buenos_Aires", google_calendar_id=None)
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            service,  # get service
            business, # get business
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        target = date(2026, 1, 15)
        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        assert len(slots) == 11
        assert slots[0].hour == 9
        assert slots[-1].hour == 19

    @patch("app.services.negocio.get_freebusy", return_value=[])
    def test_returns_empty_when_service_not_found(self, mock_gcal, mock_db):
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, None]

        slots = get_available_slots(mock_db, service_id=999, business_id=1, target_date=date(2026, 1, 15))
        assert slots == []

    @patch("app.services.negocio.get_freebusy", return_value=[])
    def test_excludes_occupied_slots(self, mock_gcal, mock_db):
        """Slots ocupados deben ser excluidos."""
        service = MagicMock(id=1, duration_minutes=30)
        business = MagicMock(id=1, timezone="America/Argentina/Buenos_Aires", google_calendar_id=None)
        target = date(2026, 1, 15)

        tz = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")
        occupied_time = datetime(2026, 1, 15, 9, 0, tzinfo=tz)
        mock_db.query.return_value.filter.return_value.first.side_effect = [service, business]
        mock_db.query.return_value.filter.return_value.all.return_value = [(occupied_time,)]

        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        assert len(slots) == 21
        assert occupied_time not in slots

    @patch("app.services.negocio.get_freebusy", return_value=[])
    def test_respects_duration_for_slots(self, mock_gcal, mock_db):
        """Slots se calculan según la duración del servicio."""
        service = MagicMock(id=1, duration_minutes=90)
        business = MagicMock(id=1, timezone="America/Argentina/Buenos_Aires", google_calendar_id=None)
        mock_db.query.return_value.filter.return_value.first.side_effect = [service, business]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        target = date(2026, 1, 15)
        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        assert len(slots) == 7

    @patch("app.services.negocio.get_freebusy", return_value=[])
    def test_uses_notin_for_cancelled(self, mock_gcal, mock_db):
        """W7: usa .notin_() en lugar de ~.in_() para cancelled."""
        service = MagicMock(id=1, duration_minutes=60)
        business = MagicMock(id=1, timezone="America/Argentina/Buenos_Aires", google_calendar_id=None)
        mock_db.query.return_value.filter.return_value.first.side_effect = [service, business]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        get_available_slots(mock_db, service_id=1, business_id=1, target_date=date(2026, 1, 15))


class TestGetBusinessTimezone:
    def test_returns_timezone_when_business_found(self, mock_db):
        business = MagicMock(timezone="America/Argentina/Buenos_Aires")
        mock_db.query.return_value.filter.return_value.first.return_value = business

        result = get_business_timezone(mock_db, business_id=1)
        assert result == "America/Argentina/Buenos_Aires"

    def test_returns_default_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_business_timezone(mock_db, business_id=999)
        assert result == "America/Argentina/Buenos_Aires"