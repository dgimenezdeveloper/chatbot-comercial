"""Modelos SQLAlchemy — capa de persistencia.

Importar todos los modelos aquí garantiza que ``Base.metadata`` los registre
para ``create_all()`` y Alembic autogenerate.
"""

from app.db.models.business import Business
from app.db.models.user import User
from app.db.models.service import Service
from app.db.models.product import Product
from app.db.models.appointment import Appointment
from app.db.models.faq import FAQ
from app.db.models.events import Event
from app.db.models.sessions import ChatSession
from app.db.models.feedback import Feedback
from app.db.models.turno_apuesta import TurnoApuesta

__all__ = [
    "Business",
    "User",
    "Service",
    "Product",
    "Appointment",
    "FAQ",
    "Event",
    "ChatSession",
    "Feedback",
    "TurnoApuesta",
]
