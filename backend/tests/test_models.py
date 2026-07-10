"""Tests de modelos SQLAlchemy — validación de columnas, PK, FK, constraints.

Verifica la estructura de los 10 modelos tras W1 (PK unification), W5 (ChatSession rename),
W6 (FK Event→ChatSession), S3 (created_at/updated_at en Event/Feedback), y C2 (UniqueConstraint).
"""

import pytest
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import func

from app.db.database import Base
from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.db.models.events import Event
from app.db.models.faq import FAQ
from app.db.models.feedback import Feedback
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.sessions import ChatSession
from app.db.models.turno_apuesta import TurnoApuesta
from app.db.models.user import User


# ============================================================================
# Helpers
# ============================================================================

def get_table(model_class):
    """Retorna el objeto Table de SQLAlchemy para un modelo."""
    return model_class.__table__


def get_columns(model_class):
    """Retorna dict: nombre → Column del modelo."""
    return {c.name: c for c in model_class.__table__.columns}


def get_fks(model_class):
    """Retorna dict: nombre_columna → ForeignKey."""
    return {
        c.name: list(c.foreign_keys)[0]
        for c in model_class.__table__.columns
        if c.foreign_keys
    }


# ============================================================================
# Business
# ============================================================================

class TestBusinessModel:
    def test_tablename(self):
        assert Business.__tablename__ == "business"

    def test_pk_id(self):
        cols = get_columns(Business)
        assert cols["id"].primary_key
        assert isinstance(cols["id"].type, Integer)

    def test_required_fields(self):
        cols = get_columns(Business)
        assert not cols["name"].nullable
        assert not cols["slug"].nullable
        assert cols["slug"].unique

    def test_optional_fields(self):
        cols = get_columns(Business)
        assert cols["description"].nullable is True
        assert cols["whatsapp_phone_id"].nullable is True

    def test_defaults(self):
        cols = get_columns(Business)
        assert cols["active"].default.arg is True
        assert cols["timezone"].default.arg == "America/Argentina/Buenos_Aires"
        assert cols["currency"].default.arg == "ARS"
        assert cols["accept_cards"].default.arg is True
        assert cols["accepts_cash"].default.arg is True

    def test_has_timestamps(self):
        cols = get_columns(Business)
        assert "created_at" in cols
        assert "updated_at" in cols
        assert isinstance(cols["created_at"].type, DateTime)
        assert cols["created_at"].type.timezone is True

    def test_is_base_subclass(self):
        assert issubclass(Business, Base)


# ============================================================================
# User
# ============================================================================

class TestUserModel:
    def test_tablename(self):
        assert User.__tablename__ == "user"

    def test_pk_id_simple(self):
        """W1: User tiene PK simple 'id'."""
        cols = get_columns(User)
        assert cols["id"].primary_key
        # Verificar que no hay composite PK
        assert len(User.__table__.primary_key.columns) == 1

    def test_business_fk(self):
        fks = get_fks(User)
        assert "business_id" in fks
        fk = fks["business_id"]
        assert fk.column.table.name == "business"
        assert fk.column.name == "id"

    def test_phone_unique_constraint(self):
        """C2: phone tiene UniqueConstraint(phone, business_id)."""
        constraints = User.__table_args__
        assert constraints is not None
        # Buscar el UniqueConstraint
        found = False
        if isinstance(constraints, tuple):
            for c in constraints:
                if isinstance(c, UniqueConstraint):
                    col_names = {col.name for col in c.columns}
                    if "phone" in col_names and "business_id" in col_names:
                        found = True
                        break
        assert found, "UniqueConstraint(phone, business_id) no encontrado"

    def test_email_unique(self):
        cols = get_columns(User)
        assert cols["email"].unique

    def test_role_enum(self):
        cols = get_columns(User)
        assert isinstance(cols["role"].type, Enum)
        assert cols["role"].default.arg == "guest"

    def test_optional_fields(self):
        cols = get_columns(User)
        assert cols["password_hash"].nullable is True
        assert cols["oauth_provider"].nullable is True

    def test_has_timestamps(self):
        cols = get_columns(User)
        assert "created_at" in cols
        assert "updated_at" in cols


# ============================================================================
# Service
# ============================================================================

class TestServiceModel:
    def test_tablename(self):
        assert Service.__tablename__ == "service"

    def test_pk_id_simple(self):
        """W1: Service tiene PK simple 'id'."""
        cols = get_columns(Service)
        assert cols["id"].primary_key
        assert len(Service.__table__.primary_key.columns) == 1

    def test_business_fk(self):
        fks = get_fks(Service)
        assert "business_id" in fks

    def test_name_required(self):
        cols = get_columns(Service)
        assert not cols["name"].nullable

    def test_slug_unique(self):
        cols = get_columns(Service)
        assert cols["slug"].unique

    def test_category_enum(self):
        cols = get_columns(Service)
        assert isinstance(cols["category"].type, Enum)

    def test_price_numeric(self):
        cols = get_columns(Service)
        assert isinstance(cols["price"].type, Numeric)


# ============================================================================
# Product
# ============================================================================

class TestProductModel:
    def test_tablename(self):
        assert Product.__tablename__ == "product"

    def test_pk_id_simple(self):
        """W1: Product tiene PK simple 'id'."""
        cols = get_columns(Product)
        assert cols["id"].primary_key
        assert len(Product.__table__.primary_key.columns) == 1

    def test_business_fk(self):
        fks = get_fks(Product)
        assert "business_id" in fks

    def test_stock_fields(self):
        cols = get_columns(Product)
        assert "stock_quantity" in cols
        assert "low_stock_threshold" in cols
        assert cols["low_stock_threshold"].default.arg == 5

    def test_slug_unique(self):
        cols = get_columns(Product)
        assert cols["slug"].unique


# ============================================================================
# Appointment
# ============================================================================

class TestAppointmentModel:
    def test_tablename(self):
        assert Appointment.__tablename__ == "appointment"

    def test_pk_id_simple(self):
        """W1: Appointment tiene PK simple 'id'."""
        cols = get_columns(Appointment)
        assert cols["id"].primary_key
        assert len(Appointment.__table__.primary_key.columns) == 1

    def test_fks(self):
        fks = get_fks(Appointment)
        assert "business_id" in fks
        assert "user_id" in fks
        assert "service_id" in fks

    def test_status_enum(self):
        cols = get_columns(Appointment)
        assert isinstance(cols["status"].type, Enum)
        assert cols["status"].default.arg == "scheduled"

    def test_scheduled_date_required(self):
        cols = get_columns(Appointment)
        assert not cols["scheduled_date"].nullable

    def test_no_show_status_enum(self):
        cols = get_columns(Appointment)
        assert "no_show_status" in cols
        assert cols["no_show_status"].nullable is True

    def test_created_via_enum(self):
        cols = get_columns(Appointment)
        assert isinstance(cols["created_via"].type, Enum)
        assert cols["created_via"].default.arg == "chatbot"


# ============================================================================
# FAQ
# ============================================================================

class TestFAQModel:
    def test_tablename(self):
        assert FAQ.__tablename__ == "faq"

    def test_pk_id(self):
        cols = get_columns(FAQ)
        assert cols["id"].primary_key

    def test_business_fk(self):
        fks = get_fks(FAQ)
        assert "business_id" in fks

    def test_question_answer_required(self):
        cols = get_columns(FAQ)
        assert not cols["question"].nullable
        assert not cols["answer"].nullable

    def test_order_field(self):
        cols = get_columns(FAQ)
        assert "order" in cols
        assert cols["order"].default.arg == 0


# ============================================================================
# ChatSession (W5: renamed from Session)
# ============================================================================

class TestChatSessionModel:
    def test_class_name_is_chat_session(self):
        """W5: El modelo se llama ChatSession."""
        assert ChatSession.__name__ == "ChatSession"

    def test_tablename_is_session(self):
        """La tabla sigue llamándose 'session'."""
        assert ChatSession.__tablename__ == "session"

    def test_pk_id(self):
        cols = get_columns(ChatSession)
        assert cols["id"].primary_key

    def test_session_id_unique(self):
        cols = get_columns(ChatSession)
        assert cols["session_id"].unique
        assert cols["session_id"].index

    def test_business_fk(self):
        fks = get_fks(ChatSession)
        assert "business_id" in fks

    def test_user_fk(self):
        fks = get_fks(ChatSession)
        assert "user_id" in fks

    def test_status_enum(self):
        cols = get_columns(ChatSession)
        assert isinstance(cols["status"].type, Enum)
        assert cols["status"].default.arg == "active"

    def test_metrics_fields(self):
        cols = get_columns(ChatSession)
        assert "n_messages_total" in cols
        assert "n_fallbacks" in cols
        assert cols["n_messages_total"].default.arg == 0
        assert cols["n_fallbacks"].default.arg == 0

    def test_has_timestamps(self):
        cols = get_columns(ChatSession)
        assert "created_at" in cols
        assert "updated_at" in cols


# ============================================================================
# Event
# ============================================================================

class TestEventModel:
    def test_tablename(self):
        assert Event.__tablename__ == "event"

    def test_pk_id(self):
        cols = get_columns(Event)
        assert cols["id"].primary_key

    def test_session_id_fk(self):
        """W6: FK de Event.session_id → ChatSession.session_id."""
        fks = get_fks(Event)
        assert "session_id" in fks
        fk = fks["session_id"]
        # La FK apunta a session.session_id
        assert fk.column.table.name == "session"
        assert fk.column.name == "session_id"

    def test_business_fk(self):
        fks = get_fks(Event)
        assert "business_id" in fks

    def test_event_type_required(self):
        cols = get_columns(Event)
        assert not cols["event_type"].nullable

    def test_payload_jsonb(self):
        cols = get_columns(Event)
        assert "payload_json" in cols
        assert isinstance(cols["payload_json"].type, JSONB)

    def test_channel_enum(self):
        cols = get_columns(Event)
        assert isinstance(cols["channel"].type, Enum)

    def test_has_created_at_updated_at(self):
        """S3: Event tiene created_at y updated_at."""
        cols = get_columns(Event)
        assert "created_at" in cols
        assert "updated_at" in cols
        assert isinstance(cols["created_at"].type, DateTime)
        assert cols["created_at"].type.timezone is True


# ============================================================================
# Feedback
# ============================================================================

class TestFeedbackModel:
    def test_tablename(self):
        assert Feedback.__tablename__ == "feedback"

    def test_pk_id(self):
        cols = get_columns(Feedback)
        assert cols["id"].primary_key

    def test_business_fk(self):
        fks = get_fks(Feedback)
        assert "business_id" in fks

    def test_score_required(self):
        cols = get_columns(Feedback)
        assert not cols["score"].nullable

    def test_session_id_required(self):
        cols = get_columns(Feedback)
        assert not cols["session_id"].nullable

    def test_outcome_enum(self):
        cols = get_columns(Feedback)
        assert "outcome" in cols
        assert isinstance(cols["outcome"].type, Enum)

    def test_has_created_at_updated_at(self):
        """S3: Feedback tiene created_at y updated_at."""
        cols = get_columns(Feedback)
        assert "created_at" in cols
        assert "updated_at" in cols


# ============================================================================
# TurnoApuesta
# ============================================================================

class TestTurnoApuestaModel:
    def test_tablename(self):
        assert TurnoApuesta.__tablename__ == "turno_apuesta"

    def test_pk_id_simple(self):
        """W1: TurnoApuesta tiene PK simple 'id'."""
        cols = get_columns(TurnoApuesta)
        assert cols["id"].primary_key
        assert len(TurnoApuesta.__table__.primary_key.columns) == 1

    def test_fks(self):
        fks = get_fks(TurnoApuesta)
        assert "business_id" in fks
        assert "appointment_id" in fks

    def test_apuesta_amount_not_null(self):
        cols = get_columns(TurnoApuesta)
        assert not cols["apuesta_amount"].nullable

    def test_status_enum(self):
        cols = get_columns(TurnoApuesta)
        assert isinstance(cols["status"].type, Enum)
        assert cols["status"].default.arg == "open"

    def test_scheduled_date_required(self):
        cols = get_columns(TurnoApuesta)
        assert not cols["scheduled_date"].nullable


# ============================================================================
# Relationships between models
# ============================================================================

class TestModelRelationships:
    """Validación de relaciones FK entre modelos."""

    def test_all_models_registered_in_base(self):
        """Todos los modelos están en Base.metadata."""
        tables = Base.metadata.tables
        expected_tables = [
            "business", "user", "service", "product",
            "appointment", "faq", "event", "session",
            "feedback", "turno_apuesta",
        ]
        for name in expected_tables:
            assert name in tables, f"Tabla '{name}' no registrada en Base.metadata"

    def test_user_belongs_to_business(self):
        fks = get_fks(User)
        assert "business_id" in fks

    def test_service_belongs_to_business(self):
        fks = get_fks(Service)
        assert "business_id" in fks

    def test_product_belongs_to_business(self):
        fks = get_fks(Product)
        assert "business_id" in fks

    def test_appointment_belongs_to_business(self):
        fks = get_fks(Appointment)
        assert "business_id" in fks

    def test_appointment_belongs_to_user(self):
        fks = get_fks(Appointment)
        assert "user_id" in fks

    def test_appointment_belongs_to_service(self):
        fks = get_fks(Appointment)
        assert "service_id" in fks

    def test_event_belongs_to_session(self):
        """W6: Event.session_id FK → ChatSession.session_id."""
        fks = get_fks(Event)
        assert "session_id" in fks

    def test_event_belongs_to_business(self):
        fks = get_fks(Event)
        assert "business_id" in fks

    def test_event_belongs_to_user(self):
        fks = get_fks(Event)
        assert "user_id" in fks

    def test_chat_session_belongs_to_business(self):
        fks = get_fks(ChatSession)
        assert "business_id" in fks

    def test_feedback_belongs_to_business(self):
        fks = get_fks(Feedback)
        assert "business_id" in fks

    def test_turno_apuesta_belongs_to_business(self):
        fks = get_fks(TurnoApuesta)
        assert "business_id" in fks

    def test_turno_apuesta_belongs_to_appointment(self):
        fks = get_fks(TurnoApuesta)
        assert "appointment_id" in fks


# ============================================================================
# Timestamp conventions
# ============================================================================

class TestTimestampConventions:
    """Verifica que todos los modelos sigan la convención de timestamps."""

    MODELS_WITH_TIMESTAMPS = [
        Business, User, Service, Product, Appointment,
        ChatSession, Event, Feedback,
    ]
    MODELS_WITHOUT_TIMESTAMPS = [FAQ, TurnoApuesta]

    @pytest.mark.parametrize("model", MODELS_WITH_TIMESTAMPS)
    def test_has_created_at(self, model):
        cols = get_columns(model)
        assert "created_at" in cols, f"{model.__name__} no tiene created_at"

    @pytest.mark.parametrize("model", MODELS_WITH_TIMESTAMPS)
    def test_has_updated_at(self, model):
        cols = get_columns(model)
        assert "updated_at" in cols, f"{model.__name__} no tiene updated_at"

    @pytest.mark.parametrize("model", MODELS_WITH_TIMESTAMPS)
    def test_created_at_is_timezone_aware(self, model):
        cols = get_columns(model)
        col = cols["created_at"]
        assert isinstance(col.type, DateTime), f"{model.__name__} created_at no es DateTime"
        assert col.type.timezone is True, f"{model.__name__} created_at no es timezone-aware"


# ============================================================================
# PK unification (W1)
# ============================================================================

class TestPKUnification:
    """Verifica que los modelos tengan PK simple (W1)."""

    MODELS_WITH_SIMPLE_PK = [Business, User, Service, Product, Appointment, FAQ, Event,
                              ChatSession, Feedback, TurnoApuesta]

    @pytest.mark.parametrize("model", MODELS_WITH_SIMPLE_PK)
    def test_single_column_pk(self, model):
        pk_cols = model.__table__.primary_key.columns
        assert len(pk_cols) == 1, (
            f"{model.__name__} tiene {len(pk_cols)} columnas en PK, se esperaba 1"
        )
        assert pk_cols[0].name == "id", (
            f"{model.__name__} PK column no se llama 'id', se llama '{pk_cols[0].name}'"
        )
