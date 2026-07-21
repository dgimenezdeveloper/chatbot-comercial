"""Fixtures compartidos para todos los tests del backend.

IMPORTANTE: Las variables de entorno DEBEN setearse antes de cualquier import
de módulos de la aplicación, ya que ``app.core.settings`` se inicializa
al importar y requiere ``DATABASE_URL`` y otras variables.
"""

import os

# ---------------------------------------------------------------------------
# Set environment variables BEFORE any app imports
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("WHATSAPP_TOKEN", "test_whatsapp_token")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test_verify_token")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "test_phone_id")
os.environ.setdefault("WHATSAPP_BUSINESS_ACCOUNT_ID", "test_waba_id")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_client_id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")

import pytest
from unittest.mock import MagicMock, create_autospec

from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Session de SQLAlchemy mockeada para tests unitarios."""
    db = create_autospec(Session, instance=True)
    return db


@pytest.fixture
def mock_query():
    """Query builder mockeado (retornado por db.query)."""
    query = MagicMock()
    # Encadenamiento común: .filter().filter()... .scalar() / .all() / .first()
    query.filter.return_value = query
    query.join.return_value = query
    query.group_by.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    return query
