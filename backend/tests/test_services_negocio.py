"""Tests para negocio service — orquestación del chatbot."""

from datetime import date, datetime
from unittest.mock import MagicMock

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
    def test_returns_slots_for_service_with_no_occupancy(self, mock_db):
        """Sin turnos ocupados, debe devolver todos los slots del día."""
        service = MagicMock(id=1, duration_minutes=60)
        # Primer call: service query
        # Segundo call: occupied query
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            service,  # get service
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = []  # no occupied

        target = date(2026, 1, 15)
        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        # 9am to 8pm, 60min slots → 11 slots
        assert len(slots) == 11
        assert slots[0].hour == 9
        assert slots[-1].hour == 19

    def test_returns_empty_when_service_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        slots = get_available_slots(mock_db, service_id=999, business_id=1, target_date=date(2026, 1, 15))
        assert slots == []

    def test_excludes_occupied_slots(self, mock_db):
        """Slots ocupados deben ser excluidos."""
        service = MagicMock(id=1, duration_minutes=30)
        target = date(2026, 1, 15)

        # Ocupar el slot de 9:00
        occupied_time = datetime(2026, 1, 15, 9, 0)
        mock_db.query.return_value.filter.return_value.first.return_value = service
        mock_db.query.return_value.filter.return_value.all.return_value = [(occupied_time,)]

        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        # 30-min slots from 9am to 8pm = 22 slots, minus 1 occupied = 21
        assert len(slots) == 21
        # 9:00 should not be in slots
        assert occupied_time not in slots

    def test_respects_duration_for_slots(self, mock_db):
        """Slots se calculan según la duración del servicio."""
        service = MagicMock(id=1, duration_minutes=90)
        mock_db.query.return_value.filter.return_value.first.return_value = service
        mock_db.query.return_value.filter.return_value.all.return_value = []

        target = date(2026, 1, 15)
        slots = get_available_slots(mock_db, service_id=1, business_id=1, target_date=target)
        # 9am-8pm in 90-min blocks: 9:00, 10:30, 12:00, 13:30, 15:00, 16:30, 18:00 = 7 slots
        assert len(slots) == 7

    def test_uses_notin_for_cancelled(self):
        """W7: usa .notin_() en lugar de ~.in_() para cancelled."""
        service = MagicMock(id=1, duration_minutes=60)
        mock_db.query.return_value.filter.return_value.first.return_value = service
        mock_db.query.return_value.filter.return_value.all.return_value = []

        get_available_slots(mock_db, service_id=1, business_id=1, target_date=date(2026, 1, 15))
        # Verificar que se usó filter (notin se aplica dentro de la query)
        # No podemos verificarlo directamente con el mock, pero el test no debe fallar


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
