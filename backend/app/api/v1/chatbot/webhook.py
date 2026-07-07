import logging
from fastapi import APIRouter, Query, Response, status
from app.core.settings import settings
from app.services.whatsapp import send_message
from app.services.state_manager import get_user_state, set_user_state

logger = logging.getLogger(__name__)
router = APIRouter()

# 1. Endpoint GET: Verificación técnica de Meta (Handshake)
@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    challenge: str = Query(None, alias="hub.challenge"),
    verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Valida la suscripción del webhook de Meta comparando el token secreto.
    """
    if mode == "subscribe" and verify_token and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook de WhatsApp verificado exitosamente por Meta.")
        return Response(content=challenge, media_type="text/plain")
    
    logger.warning("Fallo en el intento de verificación del webhook.")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)


def clean_phone_number(phone: str) -> str:
    """
    Limpia el número de teléfono para que coincida con lo que espera Meta Sandbox,
    especialmente útil para el prefijo '9' de Argentina.
    """
    if phone.startswith("549"):
        return "54" + phone[3:]
    return phone


# 2. Endpoint POST: Recepción de eventos y mensajes en tiempo real
@router.post("/webhook")
async def receive_webhook(payload: dict):
    """
    Recibe las notificaciones de eventos cuando un usuario envía un mensaje.
    """
    logger.info(f"Payload del Webhook recibido: {payload}")
    
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            phone_number = message.get("from")
            message_type = message.get("type")
            
            # --- SANITIZACIÓN DE TELÉFONO ANTES DE INTERACTUAR CON EL ESTADO ---
            # TODO: Remover este bloque al pasar a Producción con número real.
            if settings.APP_ENV == "development" and phone_number.startswith("549"):
                area_code = phone_number[3:5] 
                local_number = phone_number[5:]
                phone_number = f"54{area_code}15{local_number}"
                logger.info(f"Aplicado parche Sandbox Argentina: {phone_number}")
            else:
                phone_number = clean_phone_number(phone_number)
            
            # --- CONSULTAR ESTADO DEL USUARIO EN REDIS ---
            user_state = await get_user_state(phone_number)
            
            if not user_state:
                # Si el usuario no tiene una sesión activa, inicializamos en MENU_PRINCIPAL con paso 1
                user_state = {"estado": "MENU_PRINCIPAL", "step": 1}
                await set_user_state(phone_number, user_state)
                logger.info(f"Sesión conversacional nueva inicializada para el número {phone_number}")
            else:
                # Si ya tiene una sesión iniciada, incrementamos el paso
                user_state["step"] += 1
                await set_user_state(phone_number, user_state)
                logger.info(f"Sesión conversacional existente actualizada para el número {phone_number}: {user_state}")
            
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "")
                
                # Respuesta mock que incluye información del estado actual recuperado de Redis
                echo_text = (
                    f"Hola, soy tu chatbot. Recibí tu mensaje: '{user_text}'. "
                    f"Tu estado actual es: {user_state['estado']} (Paso conversacional: {user_state['step']})"
                )
                await send_message(phone=phone_number, text=echo_text)
                
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    return {"status": "success"}