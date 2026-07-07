import logging
import httpx
from app.core.settings import settings

logger = logging.getLogger(__name__)

async def _send_whatsapp_payload(payload: dict) -> bool:
    """Helper interno para despachar payloads JSON de forma asíncrona a la API de Meta."""
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"Mensaje de WhatsApp despachado de forma exitosa a {payload.get('to')}")
                return True
            else:
                logger.error(f"Error al enviar mensaje de WhatsApp. Estatus: {response.status_code}. Respuesta: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al conectar con la API de Meta: {str(e)}")
            return False

async def send_message(phone: str, text: str) -> bool:
    """Envía un mensaje de texto plano estándar."""
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
    return await _send_whatsapp_payload(payload)

async def send_interactive_buttons(phone: str, body_text: str, buttons: list) -> bool:
    """
    Envía un mensaje interactivo con hasta 3 botones de respuesta rápida (Reply Buttons).
    Estructura esperada de 'buttons': [{'id': 'btn_id', 'title': 'Título'}]
    """
    if len(buttons) > 3:
        logger.warning(f"Se recibieron {len(buttons)} botones. WhatsApp permite un máximo de 3. Truncando lista.")
        buttons = buttons[:3]

    formatted_buttons = []
    for btn in buttons:
        formatted_buttons.append({
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"][:20]  # Meta restringe a máximo 20 caracteres
            }
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": formatted_buttons
            }
        }
    }
    return await _send_whatsapp_payload(payload)

async def send_interactive_list(
    phone: str,
    body_text: str,
    button_label: str,
    sections: list,
    header_text: str = None,
    footer_text: str = None
) -> bool:
    """
    Envía un menú de lista desplegable (List Message) de hasta 10 opciones totales.
    Estructura esperada de 'sections':
    [
        {
            "title": "Sección Principal",
            "rows": [
                {"id": "srv_1", "title": "Corte", "description": "Descripción opcional"}
            ]
        }
    ]
    """
    formatted_sections = []
    total_rows = 0
    
    for sec in sections:
        section_rows = []
        for row in sec.get("rows", []):
            if total_rows >= 10:
                logger.warning("Límite máximo de 10 opciones totales alcanzado. Omitiendo filas restantes.")
                break
                
            row_data = {
                "id": row["id"],
                "title": row["title"][:24]  # Meta restringe a máximo 24 caracteres
            }
            if row.get("description"):
                row_data["description"] = row["description"][:72]  # Meta restringe a máximo 72 caracteres
                
            section_rows.append(row_data)
            total_rows += 1
            
        formatted_sections.append({
            "title": sec.get("title", "")[:20],  # Meta restringe a máximo 20 caracteres
            "rows": section_rows
        })

    interactive_payload = {
        "type": "list",
        "body": {
            "text": body_text
        },
        "action": {
            "button": button_label[:20],  # Meta restringe el label del botón a máximo 20 caracteres
            "sections": formatted_sections
        }
    }

    if header_text:
        interactive_payload["header"] = {
            "type": "text",
            "text": header_text[:60]  # Meta restringe el header a máximo 60 caracteres
        }
    if footer_text:
        interactive_payload["footer"] = {
            "text": footer_text[:60]  # Meta restringe el footer a máximo 60 caracteres
        }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": interactive_payload
    }
    return await _send_whatsapp_payload(payload)