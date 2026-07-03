import logging
from fastapi import APIRouter, Query, Response, status
from app.core.settings import settings
from app.services.whatsapp import send_message

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
    if mode == "subscribe" and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook de WhatsApp verificado exitosamente por Meta.")
        return Response(content=challenge, media_type="text/plain")
    
    logger.warning("Fallo en el intento de verificación del webhook.")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)


def clean_phone_number(phone: str) -> str:
    """
    Limpia el número de teléfono para que coincida con lo que espera Meta Sandbox,
    especialmente útil para el prefijo '9' de Argentina.
    """
    # Si es Argentina (54) y tiene el '9' después del código de país, se lo quitamos.
    # Meta Sandbox suele registrar los números sin ese 9.
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
        # Navegación defensiva del payload de Meta
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            phone_number = message.get("from")
            message_type = message.get("type")
            
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "")
                phone_number = message.get("from")
                
                # --- FIX TEMPORAL: ARGENTINA SANDBOX ---
                # TODO: Remover este bloque al pasar a Producción con número real.
                # El Sandbox de Meta tiene un bug con el formato de numeración en Argentina.
                if settings.APP_ENV == "development" and phone_number.startswith("549"):
                    area_code = phone_number[3:5] 
                    local_number = phone_number[5:]
                    phone_number = f"54{area_code}15{local_number}"
                    logger.info(f"Aplicado parche Sandbox Argentina: {phone_number}")
                # ---------------------------------------

                echo_text = f"Hola, soy tu chatbot. Recibí tu mensaje: '{user_text}'"
                await send_message(phone=phone_number, text=echo_text)
                
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    # Meta exige retornar siempre HTTP 200 rápidamente para confirmar recepción
    return {"status": "success"}