"""Helper de persistencia de eventos para métricas.

Provee ``log_event()``, una función fire-and-forget que registra eventos
instrumentados en la tabla ``event`` sin interrumpir el flujo del webhook.
"""

import logging
from typing import Optional

from app.db.database import SessionLocal
from app.db.models.events import Event

logger = logging.getLogger(__name__)


def log_event(
    session_id: str,
    business_id: int,
    event_type: str,
    payload: Optional[dict] = None,
    user_id: Optional[int] = None,
    channel: str = "whatsapp",
) -> Optional[Event]:
    """Registra un evento de métrica en la base de datos.

    La función es **fire-and-forget**: si algo falla, loguea el error y
    retorna ``None``, pero nunca lanza una excepción hacia arriba para no
    interrumpir el flujo del webhook.

    Args:
        session_id: ID único de la sesión de WhatsApp.
        business_id: ID del negocio multi-tenant.
        event_type: Tipo de evento (ej: ``conversation_started``).
        payload: Diccionario con datos específicos del evento (se guarda como JSONB).
        user_id: ID de usuario registrado (opcional).
        channel: Canal de origen (default ``whatsapp``).

    Returns:
        El objeto ``Event`` creado, o ``None`` si falló la persistencia.
    """
    db = SessionLocal()
    try:
        event = Event(
            session_id=session_id,
            business_id=business_id,
            event_type=event_type,
            payload_json=payload,
            user_id=user_id,
            channel=channel,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        logger.debug("Evento registrado: type=%s session=%s", event_type, session_id)
        return event
    except Exception:
        logger.exception(
            "Error al persistir evento type=%s session=%s", event_type, session_id
        )
        db.rollback()
        return None
    finally:
        db.close()
