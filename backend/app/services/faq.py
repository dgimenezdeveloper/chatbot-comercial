"""Servicio CRUD para preguntas frecuentes (FAQ).

Operaciones contra PostgreSQL usando SQLAlchemy Session.
Incluye búsqueda por texto y filtrado por categoría.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.faq import FAQ

logger = logging.getLogger(__name__)


def get_faqs(db: Session, business_id: int) -> list[FAQ]:
    """Lista todas las FAQs activas de un negocio, ordenadas por order."""
    return (
        db.query(FAQ)
        .filter(FAQ.business_id == business_id, FAQ.is_active.is_(True))
        .order_by(FAQ.order, FAQ.id)
        .all()
    )


def get_faq(db: Session, faq_id: int) -> Optional[FAQ]:
    """Obtiene una FAQ por ID."""
    return db.query(FAQ).filter(FAQ.id == faq_id).first()


def create_faq(db: Session, data: dict) -> FAQ:
    """Crea una nueva FAQ y la persiste."""
    faq = FAQ(**data)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    logger.info("FAQ creada: id=%s question=%s", faq.id, faq.question[:50])
    return faq


def update_faq(db: Session, faq_id: int, data: dict) -> Optional[FAQ]:
    """Actualiza una FAQ existente. Retorna None si no existe."""
    faq = get_faq(db, faq_id)
    if not faq:
        return None
    for key, value in data.items():
        setattr(faq, key, value)
    db.commit()
    db.refresh(faq)
    logger.info("FAQ actualizada: id=%s", faq.id)
    return faq


def delete_faq(db: Session, faq_id: int) -> bool:
    """Soft-delete: desactiva la FAQ (is_active=False)."""
    faq = get_faq(db, faq_id)
    if not faq:
        return False
    faq.is_active = False
    db.commit()
    logger.info("FAQ desactivada: id=%s", faq.id)
    return True


def search_faqs(db: Session, business_id: int, query: str) -> list[FAQ]:
    """Busca FAQs por texto en pregunta y respuesta (ILIKE, case-insensitive)."""
    search_term = f"%{query}%"
    return (
        db.query(FAQ)
        .filter(
            FAQ.business_id == business_id,
            FAQ.is_active.is_(True),
            (FAQ.question.ilike(search_term) | FAQ.answer.ilike(search_term)),
        )
        .order_by(FAQ.order, FAQ.id)
        .all()
    )


def get_faqs_by_category(db: Session, business_id: int, category: str) -> list[FAQ]:
    """Lista FAQs activas filtradas por categoría."""
    return (
        db.query(FAQ)
        .filter(
            FAQ.business_id == business_id,
            FAQ.is_active.is_(True),
            FAQ.category == category,
        )
        .order_by(FAQ.order, FAQ.id)
        .all()
    )
