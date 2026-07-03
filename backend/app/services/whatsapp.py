import logging
import httpx
from app.core.settings import settings

logger = logging.getLogger(__name__)

async def send_message(phone: str, text: str) -> bool:
    """
    Envía un mensaje de texto de manera asíncrona usando la API Cloud de WhatsApp de Meta.
    """
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"Mensaje enviado exitosamente a {phone}")
                return True
            else:
                logger.error(f"Error al enviar mensaje a {phone}: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al conectar con la API de Meta: {str(e)}")
            return False