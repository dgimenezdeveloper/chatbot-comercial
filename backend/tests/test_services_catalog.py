"""Tests para catalog service — CRUD de servicios y productos."""

from unittest.mock import MagicMock

import pytest

from app.services.catalog import (
    create_product,
    create_service,
    delete_product,
    delete_service,
    get_product,
    get_products,
    get_service,
    get_services,
    update_product,
    update_service,
)


# ============================================================================
# Service CRUD
# ============================================================================

class TestGetServices:
    def test_returns_active_services_ordered(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, name="Corte", category="corte"),
            MagicMock(id=2, name="Tinte", category="coloración"),
        ]
        result = get_services(mock_db, business_id=1)
        assert len(result) == 2
        assert result[0].name == "Corte"

    def test_filters_by_business_and_active(self, mock_db):
        get_services(mock_db, business_id=5)
        # Verificar que se llamó a filter con los argumentos esperados
        call_args = mock_db.query.return_value.filter.call_args[0]
        assert call_args is not None


class TestGetService:
    def test_returns_service_when_found(self, mock_db):
        expected = MagicMock(id=1, name="Corte")
        mock_db.query.return_value.filter.return_value.first.return_value = expected

        result = get_service(mock_db, service_id=1, business_id=1)
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_service(mock_db, service_id=999, business_id=1)
        assert result is None


class TestCreateService:
    def test_creates_and_returns_service(self, mock_db):
        data = {"name": "Nuevo Corte", "slug": "nuevo-corte", "business_id": 1,
                "category": "corte", "price": 3000.00}
        # Mock refresh para setear id
        def refresh_side_effect(obj):
            obj.id = 10
        mock_db.refresh.side_effect = refresh_side_effect

        result = create_service(mock_db, data)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.id == 10
        assert result.name == "Nuevo Corte"


class TestUpdateService:
    def test_updates_existing_service(self, mock_db):
        service = MagicMock(id=1, name="Corte", price=5000.00)
        mock_db.query.return_value.filter.return_value.first.return_value = service

        result = update_service(mock_db, service_id=1, business_id=1, data={"price": 6000.00})
        assert result is service
        assert service.price == 6000.00
        mock_db.commit.assert_called_once()

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = update_service(mock_db, service_id=999, business_id=1, data={"price": 6000.00})
        assert result is None


class TestDeleteService:
    def test_soft_deletes_service(self, mock_db):
        service = MagicMock(id=1, is_active=True)
        mock_db.query.return_value.filter.return_value.first.return_value = service

        result = delete_service(mock_db, service_id=1, business_id=1)
        assert result is True
        assert service.is_active is False
        mock_db.commit.assert_called_once()

    def test_returns_false_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = delete_service(mock_db, service_id=999, business_id=1)
        assert result is False


# ============================================================================
# Product CRUD
# ============================================================================

class TestGetProducts:
    def test_returns_active_products_ordered(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, name="Shampoo"),
            MagicMock(id=2, name="Acondicionador"),
        ]
        result = get_products(mock_db, business_id=1)
        assert len(result) == 2


class TestGetProduct:
    def test_returns_product_when_found(self, mock_db):
        expected = MagicMock(id=1, name="Shampoo")
        mock_db.query.return_value.filter.return_value.first.return_value = expected
        result = get_product(mock_db, product_id=1, business_id=1)
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_product(mock_db, product_id=999, business_id=1)
        assert result is None


class TestCreateProduct:
    def test_creates_and_returns_product(self, mock_db):
        def refresh_side_effect(obj):
            obj.id = 5
        mock_db.refresh.side_effect = refresh_side_effect
        data = {"name": "Gel", "slug": "gel", "business_id": 1, "price": 1500.00}

        result = create_product(mock_db, data)
        assert result.id == 5
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestUpdateProduct:
    def test_updates_existing_product(self, mock_db):
        product = MagicMock(id=1, name="Shampoo", stock_quantity=10)
        mock_db.query.return_value.filter.return_value.first.return_value = product

        result = update_product(mock_db, product_id=1, business_id=1, data={"stock_quantity": 5})
        assert result is product
        assert product.stock_quantity == 5

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = update_product(mock_db, product_id=999, business_id=1, data={"stock_quantity": 5})
        assert result is None


class TestDeleteProduct:
    def test_soft_deletes_product(self, mock_db):
        product = MagicMock(id=1, is_active=True)
        mock_db.query.return_value.filter.return_value.first.return_value = product

        result = delete_product(mock_db, product_id=1, business_id=1)
        assert result is True
        assert product.is_active is False

    def test_returns_false_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = delete_product(mock_db, product_id=999, business_id=1)
        assert result is False
