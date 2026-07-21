"""Tests para data_seed — funciones de seed data idempotente."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.data_seed import (
    main,
    seed_admin_user,
    seed_business,
    seed_faqs,
    seed_products,
    seed_services,
)


class TestSeedBusiness:
    def test_creates_business_when_not_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_business(mock_db)
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    def test_returns_existing_business(self, mock_db):
        existing = MagicMock(id=1, name="Salon Demo Belén", slug="salon-demo-belen")
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        result = seed_business(mock_db)
        assert result is existing
        mock_db.add.assert_not_called()


class TestSeedServices:
    def test_creates_services_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_services(mock_db, business_id=1)
        assert len(result) == 8  # 8 servicios en seed data
        mock_db.commit.assert_called()

    def test_skips_when_services_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = seed_services(mock_db, business_id=1)
        assert result == []
        mock_db.add.assert_not_called()


class TestSeedProducts:
    def test_creates_products_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_products(mock_db, business_id=1)
        assert len(result) == 4  # 4 productos en seed data
        mock_db.commit.assert_called()

    def test_skips_when_products_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = seed_products(mock_db, business_id=1)
        assert result == []


class TestSeedFaqs:
    def test_creates_faqs_when_none_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_faqs(mock_db, business_id=1)
        assert len(result) == 6  # 6 FAQs en seed data
        mock_db.commit.assert_called()

    def test_skips_when_faqs_exist(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = seed_faqs(mock_db, business_id=1)
        assert result == []


class TestSeedAdminUser:
    def test_creates_admin_when_not_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = seed_admin_user(mock_db, business_id=1)
        assert result is not None
        assert result.role == "admin"
        mock_db.add.assert_called_once()

    def test_returns_existing_admin(self, mock_db):
        existing = MagicMock(id=42, email="admin@salondemo.com", role="admin")
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        result = seed_admin_user(mock_db, business_id=1)
        assert result is existing
        mock_db.add.assert_not_called()


class TestMainOrchestrator:
    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.seed_business")
    @patch("app.data_seed.seed_services")
    @patch("app.data_seed.seed_products")
    @patch("app.data_seed.seed_faqs")
    @patch("app.data_seed.seed_admin_user")
    def test_runs_all_seed_functions(
        self, mock_admin, mock_faqs, mock_products, mock_services, mock_business, mock_session
    ):
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_business.return_value = MagicMock(id=1)

        main()

        # Cada seed function fue llamada
        mock_business.assert_called_once_with(mock_db)
        mock_services.assert_called_once_with(mock_db, 1)
        mock_products.assert_called_once_with(mock_db, 1)
        mock_faqs.assert_called_once_with(mock_db, 1)
        mock_admin.assert_called_once_with(mock_db, 1)

        # DB session se cerró
        mock_db.close.assert_called_once()

    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.seed_business")
    def test_handles_integrity_error(self, mock_business, mock_session):
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_business.side_effect = IntegrityError("duplicate", None, None)

        # No debe propagar la excepción
        main()
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.data_seed.SessionLocal")
    @patch("app.data_seed.seed_business")
    def test_rollback_and_close_on_exception(self, mock_business, mock_session):
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_business.side_effect = RuntimeError("unexpected")

        with pytest.raises(RuntimeError):
            main()
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()
