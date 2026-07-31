import logging
import httpx
from app.core.settings import settings

logger = logging.getLogger(__name__)

def get_whatsapp_phone_variants(phone: str) -> list[str]:
    """Genera las 3 variantes de formato de Argentina para garantizar la entrega en Meta Sandbox o Producción."""
    digits = "".join(c for c in phone if c.isdigit())
    if not digits:
        return []
    
    if not digits.startswith("54"):
        return [digits]

    # Extraer base local (últimos 8 dígitos)
    if len(digits) >= 10:
        local_8 = digits[-8:]
        area = digits[-10:-8] # ej: "11"
        
        base_no_15 = local_8
        
        variants = [
            digits,                                # El original (ej: 5491169695436)
            f"54{area}{base_no_15}",               # Formato sin 9 (ej: 541169695436)
            f"541115{base_no_15}" if area == "11" else f"54{area}15{base_no_15}", # Formato Sandbox Meta con 15 (ej: 54111569695436)
            f"549{area}{base_no_15}",              # Formato Prod con 9
        ]
        return list(dict.fromkeys(variants))
    
    return [digits]

async def _send_whatsapp_payload(payload: dict) -> bool:
    """Helper interno para despachar payloads JSON de forma asíncrona a la API de Meta."""
    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    original_to = str(payload.get("to", ""))
    variants = get_whatsapp_phone_variants(original_to)
    
    async with httpx.AsyncClient() as client:
        for target_phone in variants:
            payload["to"] = target_phone
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    logger.info(f"Mensaje de WhatsApp despachado con éxito a {target_phone}")
                    return True
                else:
                    logger.warning(f"Intento de envío a {target_phone} falló ({response.status_code}): {response.json().get('error', {}).get('message')}")
            except Exception as e:
                logger.error(f"Excepción enviando a {target_phone}: {e}")

        logger.error(f"Todos los intentos de envío fallaron para el número base {original_to}")
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
    """Envía un mensaje interactivo con hasta 3 botones de respuesta rápida."""
    if len(buttons) > 3:
        buttons = buttons[:3]

    formatted_buttons = []
    for btn in buttons:
        formatted_buttons.append({
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"][:20]
            }
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": formatted_buttons}
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
    """Envía un menú de lista desplegable de hasta 10 opciones totales."""
    formatted_sections = []
    total_rows = 0
    
    for sec in sections:
        section_rows = []
        for row in sec.get("rows", []):
            if total_rows >= 10:
                break
                
            row_data = {
                "id": row["id"],
                "title": row["title"][:24]
            }
            if row.get("description"):
                row_data["description"] = row["description"][:72]
                
            section_rows.append(row_data)
            total_rows += 1
            
        formatted_sections.append({
            "title": sec.get("title", "")[:20],
            "rows": section_rows
        })

    interactive_payload = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_label[:20],
            "sections": formatted_sections
        }
    }

    if header_text:
        interactive_payload["header"] = {"type": "text", "text": header_text[:60]}
    if footer_text:
        interactive_payload["footer"] = {"text": footer_text[:60]}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": interactive_payload
    }
    return await _send_whatsapp_payload(payload)