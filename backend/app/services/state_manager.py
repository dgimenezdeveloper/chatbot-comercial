import json
import logging
import random
from typing import Any, Dict, Optional
import redis.asyncio as redis
from app.core.settings import settings

logger = logging.getLogger(__name__)

# Inicializar cliente asíncrono de Redis usando la URI de configuración
redis_client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

SESSION_PREFIX = "waba_session"

async def get_user_state(phone: str) -> Optional[Dict[str, Any]]:
    """Recupera el estado conversacional actual del usuario desde Redis."""
    key = f"{SESSION_PREFIX}:{phone}"
    try:
        state_json = await redis_client.get(key)
        if state_json:
            return json.loads(state_json)
        return None
    except Exception as e:
        logger.error(f"Error al obtener el estado conversacional para {phone} de Redis: {str(e)}")
        return None

async def set_user_state(phone: str, state_data: dict, ttl: int = 86400) -> None:
    """Almacena el estado conversacional del usuario en Redis."""
    key = f"{SESSION_PREFIX}:{phone}"
    try:
        state_json = json.dumps(state_data)
        await redis_client.setex(key, ttl, state_json)
        logger.info(f"Estado conversacional guardado en Redis para {phone}: {state_data}")
    except Exception as e:
        logger.error(f"Error al persistir el estado de Redis para {phone}: {str(e)}")

async def clear_user_state(phone: str) -> None:
    """Elimina el estado de la sesión actual del usuario."""
    key = f"{SESSION_PREFIX}:{phone}"
    try:
        await redis_client.delete(key)
        logger.info(f"Estado de Redis eliminado con éxito para {phone}")
    except Exception as e:
        logger.error(f"Error al eliminar el estado conversacional de Redis para {phone}: {str(e)}")

# =============================================================================
# PROXY PARA DERIVACIÓN HUMANA (HANDOVER PROTOCOL)
# =============================================================================

async def create_human_proxy(business_id: int, client_phone: str, ttl: int = 43200) -> str:
    """Crea un ID corto de 3 dígitos (100-999) y mapea Cliente <-> Dueño en Redis por 12hs."""
    try:
        existing_id = await redis_client.get(f"proxy_rev:{client_phone}")
        if existing_id:
            return existing_id

        while True:
            short_id = str(random.randint(100, 999))
            exists = await redis_client.exists(f"proxy:{business_id}:{short_id}")
            if not exists:
                break

        await redis_client.setex(f"proxy:{business_id}:{short_id}", ttl, client_phone)
        await redis_client.setex(f"proxy_rev:{client_phone}", ttl, short_id)
        return short_id
    except Exception as e:
        logger.error(f"Error al crear proxy en Redis: {e}")
        return "100"

async def get_client_by_short_id(business_id: int, short_id: str) -> Optional[str]:
    """Obtiene el teléfono del cliente a partir del ID corto enviado por el dueño."""
    try:
        return await redis_client.get(f"proxy:{business_id}:{short_id}")
    except Exception as e:
        logger.error(f"Error al obtener cliente por ID corto en Redis: {e}")
        return None

async def close_human_proxy(business_id: int, short_id: str) -> Optional[str]:
    """Elimina el mapeo del proxy y retorna el teléfono del cliente."""
    try:
        client_phone = await redis_client.get(f"proxy:{business_id}:{short_id}")
        if client_phone:
            await redis_client.delete(f"proxy:{business_id}:{short_id}")
            await redis_client.delete(f"proxy_rev:{client_phone}")
        return client_phone
    except Exception as e:
        logger.error(f"Error al cerrar proxy en Redis: {e}")
        return None