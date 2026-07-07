import logging
from fastapi import APIRouter, Query, Response, status
from app.core.settings import settings
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import get_user_state, set_user_state, clear_user_state

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
            
            # Sanitización de número de teléfono
            if settings.APP_ENV == "development" and phone_number.startswith("549"):
                area_code = phone_number[3:5] 
                local_number = phone_number[5:]
                phone_number = f"54{area_code}15{local_number}"
                logger.info(f"Aplicado parche Sandbox Argentina: {phone_number}")
            else:
                phone_number = clean_phone_number(phone_number)
            
            # Consultar o inicializar estado conversacional del usuario
            user_state = await get_user_state(phone_number)
            if not user_state:
                user_state = {"estado": "MENU_PRINCIPAL", "step": 1}
                await set_user_state(phone_number, user_state)
            
            # --- PARSEO DE EVENTOS SEGÚN SU TIPO ---
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()
                logger.info(f"Mensaje de texto de {phone_number}: '{user_text}'")
                
                # Soportar comandos rápidos para reiniciar conversación o invocar el menú
                if user_text.lower() in ["hola", "menu", "menú", "volver", "comenzar"]:
                    await clear_user_state(phone_number)
                    user_state = {"estado": "MENU_PRINCIPAL", "step": 1}
                    await set_user_state(phone_number, user_state)
                    
                    botones_principales = [
                        {"id": "btn_turnos", "title": "📅 Turnos"},
                        {"id": "btn_catalogo", "title": "🛍️ Catálogo"},
                        {"id": "btn_faq", "title": "❓ FAQ"}
                    ]
                    await send_interactive_buttons(
                        phone=phone_number,
                        body_text="¡Hola! Bienvenido a la Peluquería Estilo. ¿En qué podemos ayudarte hoy?",
                        buttons=botones_principales
                    )
                else:
                    await send_message(
                        phone=phone_number,
                        text="Disculpa, por ahora no comprendo texto libre 😅. Escribe 'Menú' para interactuar usando mis botones."
                    )
                    
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")
                
                if interactive_type == "button_reply":
                    reply = interactive_data.get("button_reply", {})
                    selected_id = reply.get("id")
                    button_title = reply.get("title", "")
                    logger.info(f"Botón presionado por {phone_number}: ID={selected_id}, Título='{button_title}'")
                    
                    # --- COMPORTAMIENTO DE ENRUTAMIENTO (ÁRBOL CONVERSACIONAL) ---
                    if selected_id == "btn_turnos":
                        user_state["estado"] = "MENU_TURNOS"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        botones_turnos = [
                            {"id": "btn_turno_reservar", "title": "➕ Reservar"},
                            {"id": "btn_turno_ver", "title": "👀 Ver próximo"},
                            {"id": "btn_turno_cancelar", "title": "❌ Cancelar"}
                        ]
                        await send_interactive_buttons(
                            phone=phone_number,
                            body_text="Perfecto. Aquí tienes las opciones para gestionar tus turnos:",
                            buttons=botones_turnos
                        )
                        
                    elif selected_id == "btn_catalogo":
                        user_state["estado"] = "MENU_CATALOGO"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        # Definición de lista con secciones y opciones individuales
                        secciones_catalogo = [
                            {
                                "title": "Servicios Populares",
                                "rows": [
                                    {"id": "srv_corte", "title": "Corte Masculino", "description": "Corte clásico o moderno - 30 min"},
                                    {"id": "srv_barba", "title": "Perfilado Barba", "description": "Arreglo con toalla caliente - 20 min"},
                                    {"id": "srv_tintura", "title": "Tintura", "description": "Coloración completa premium - 60 min"}
                                ]
                            }
                        ]
                        await send_interactive_list(
                            phone=phone_number,
                            body_text="Por favor, selecciona una de las opciones del menú para conocer más detalles y precios de nuestros servicios:",
                            button_label="Ver catálogo 🛍️",
                            sections=secciones_catalogo,
                            header_text="Nuestro Catálogo",
                            footer_text="Peluquería Estilo"
                        )
                        
                    elif selected_id == "btn_faq":
                        user_state["estado"] = "ESPERANDO_FAQ"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        await send_message(
                            phone=phone_number,
                            text="Por favor, escribe tu consulta (por ejemplo: ¿Aceptan tarjetas?)."
                        )
                        
                    # --- GESTIÓN DE SUB-OPCIONES (TURNOS) ---
                    elif selected_id == "btn_turno_reservar":
                        await send_message(
                            phone=phone_number,
                            text="Has seleccionado Reservar un Turno. (Próximamente mostraremos los horarios disponibles)."
                        )
                        await clear_user_state(phone_number)
                        
                    elif selected_id == "btn_turno_ver":
                        await send_message(
                            phone=phone_number,
                            text="Buscando tus reservas... Actualmente tienes un turno agendado para mañana a las 10:00 hs."
                        )
                        await clear_user_state(phone_number)
                        
                    elif selected_id == "btn_turno_cancelar":
                        await send_message(
                            phone=phone_number,
                            text="Tu último turno ha sido cancelado con éxito. El horario ha quedado liberado."
                        )
                        await clear_user_state(phone_number)
                        
                elif interactive_type == "list_reply":
                    reply = interactive_data.get("list_reply", {})
                    selected_id = reply.get("id")
                    row_title = reply.get("title", "")
                    logger.info(f"Opción de lista seleccionada por {phone_number}: ID={selected_id}, Título='{row_title}'")
                    
                    if selected_id.startswith("srv_"):
                        await send_message(
                            phone=phone_number,
                            text=f"Excelente elección: '{row_title}'. Puedes reservar este servicio desde la opción 'Turnos' de nuestro Menú Principal."
                        )
                        await clear_user_state(phone_number)
                        
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    return {"status": "success"}