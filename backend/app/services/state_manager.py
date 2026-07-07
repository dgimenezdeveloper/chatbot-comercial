import json
import logging
from typing import Any, Dict, Optional
import redis.asyncio as redis
from app.core.settings import settings

logger = logging.getLogger(__name__)

# Inicializar cliente asíncrono de Redis usando la URI de configuración
redis_client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

SESSION_PREFIX = "waba_session"

async def get_user_state(phone: str) -> Optional[Dict[str, Any]]:
    """
    Recupera el estado conversacional actual del usuario desde Redis.
    Retorna un diccionario deserializado si existe, o None si no.
    """
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
    """
    Almacena el estado conversacional del usuario en Redis.
    Por defecto, expira en 24 horas (86400 segundos) para coincidir con la ventana CSW de Meta.
    """
    key = f"{SESSION_PREFIX}:{phone}"
    try:
        state_json = json.dumps(state_data)
        await redis_client.setex(key, ttl, state_json)
        logger.info(f"Estado conversacional guardado en Redis para {phone}: {state_data}")
    except Exception as e:
        logger.error(f"Error al persistir el estado de Redis para {phone}: {str(e)}")

async def clear_user_state(phone: str) -> None:
    """
    Elimina el estado de la sesión actual del usuario.
    """
    key = f"{SESSION_PREFIX}:{phone}"
    try:
        await redis_client.delete(key)
        logger.info(f"Estado de Redis eliminado con éxito para {phone}")
    except Exception as e:
        logger.error(f"Error al eliminar el estado conversacional de Redis para {phone}: {str(e)}")