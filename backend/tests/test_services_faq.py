"""Tests para FAQ service — CRUD + búsqueda."""

from unittest.mock import MagicMock

import pytest

from app.services.faq import (
    create_faq,
    delete_faq,
    get_faq,
    get_faqs,
    get_faqs_by_category,
    search_faqs,
    update_faq,
)


class TestGetFaqs:
    def test_returns_active_faqs_ordered(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, question="¿Precio?", order=1),
            MagicMock(id=2, question="¿Horario?", order=2),
        ]
        result = get_faqs(mock_db, business_id=1)
        assert len(result) == 2


class TestGetFaq:
    def test_returns_faq_when_found(self, mock_db):
        expected = MagicMock(id=1, question="¿Precio?")
        mock_db.query.return_value.filter.return_value.first.return_value = expected
        result = get_faq(mock_db, faq_id=1)
        assert result is expected

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_faq(mock_db, faq_id=999)
        assert result is None


class TestCreateFaq:
    def test_creates_and_returns_faq(self, mock_db):
        def refresh_side_effect(obj):
            obj.id = 10
        mock_db.refresh.side_effect = refresh_side_effect
        data = {"business_id": 1, "question": "¿Nueva?", "answer": "Sí"}

        result = create_faq(mock_db, data)
        assert result.id == 10
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestUpdateFaq:
    def test_updates_existing_faq(self, mock_db):
        faq = MagicMock(id=1, question="Old", answer="Old answer")
        mock_db.query.return_value.filter.return_value.first.return_value = faq

        result = update_faq(mock_db, faq_id=1, data={"question": "New", "answer": "New answer"})
        assert result is faq
        assert faq.question == "New"
        mock_db.commit.assert_called_once()

    def test_returns_none_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = update_faq(mock_db, faq_id=999, data={"question": "x"})
        assert result is None


class TestDeleteFaq:
    def test_soft_deletes_faq(self, mock_db):
        faq = MagicMock(id=1, is_active=True)
        mock_db.query.return_value.filter.return_value.first.return_value = faq

        result = delete_faq(mock_db, faq_id=1)
        assert result is True
        assert faq.is_active is False

    def test_returns_false_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = delete_faq(mock_db, faq_id=999)
        assert result is False


class TestSearchFaqs:
    def test_returns_matching_faqs(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, question="¿Precio del corte?"),
        ]
        result = search_faqs(mock_db, business_id=1, query="precio")
        assert len(result) == 1

    def test_returns_empty_when_no_match(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = search_faqs(mock_db, business_id=1, query="zzzzz")
        assert result == []


class TestGetFaqsByCategory:
    def test_returns_faqs_for_category(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            MagicMock(id=1, category="turnos"),
            MagicMock(id=2, category="turnos"),
        ]
        result = get_faqs_by_category(mock_db, business_id=1, category="turnos")
        assert len(result) == 2
