"""Tests para data_seed — funciones de seed data idempotente."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.data_seed import (
    main,
    run_basic_seed,
    seed_admin_users,
    seed_businesses,
    seed_faqs,
    seed_products,
    seed_services,
)


class TestSeedBusinesses:
    def test_creates_businesses_when_not_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        b1, b2 = seed_businesses(mock_db)
        assert b1 is not None
        assert b2 is not None
        assert mock_db.add.call_count == 2
        assert mock_db.commit.call_count >= 2

    def test_returns_existing_businesses(self, mock_db):
        existing1 = MagicMock(id=1, name="Salon Demo Belén", slug="salon-demo-belen")
        existing2 = MagicMock(id=2, name="Barbería Innova", slug="barberia-innova")
        mock_db.query.return_value.filter.return_value.first.side_effect = [existing1, existing2]

        b1, b2 = seed_businesses(mock_db)
        assert b1 is existing1
        assert b2 is existing2


class TestSeedServices:
    def test_creates_services_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_services(mock_db, business_id=1)
        assert len(result) == 8
        mock_db.commit.assert_called()

    def test_skips_when_services_exist(self, mock_db):
        mock_svc = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_svc
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_svc]

        result = seed_services(mock_db, business_id=1)
        assert len(result) >= 1


class TestSeedProducts:
    def test_creates_products_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_products(mock_db, business_id=1)
        assert len(result) == 4
        mock_db.commit.assert_called()

    def test_skips_when_products_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = seed_products(mock_db, business_id=1)
        assert result == []


class TestSeedFaqs:
    def test_creates_faqs_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_faqs(mock_db, business_id=1)
        assert len(result) == 6
        mock_db.commit.assert_called()

    def test_skips_when_faqs_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = seed_faqs(mock_db, business_id=1)
        assert result == []


class TestSeedAdminUsers:
    def test_creates_admins_when_not_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        seed_admin_users(mock_db, b1_id=1, b2_id=2)
        assert mock_db.add.call_count > 0
        mock_db.commit.assert_called()


class TestMainOrchestrator:
    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.run_basic_seed")
    def test_runs_basic_seed_default(self, mock_basic, mock_session):
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        main()

        mock_basic.assert_called_once_with(mock_db)
        mock_db.close.assert_called_once()

    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.run_basic_seed")
    def test_handles_integrity_error(self, mock_basic, mock_session):
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_basic.side_effect = IntegrityError("duplicate", None, None)

        main()
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.run_basic_seed")
    def test_rollback_and_close_on_exception(self, mock_basic, mock_session):
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_basic.side_effect = RuntimeError("unexpected")

        with pytest.raises(RuntimeError):
            main()
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()