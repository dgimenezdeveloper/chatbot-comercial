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
    if mode == "subscribe" and verify_token and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook de WhatsApp verificado exitosamente por Meta.")
        return Response(content=challenge, media_type="text/plain")
    
    logger.warning("Fallo en el intento de verificación del webhook.")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)


def clean_phone_number(phone: str) -> str:
    if phone.startswith("549"):
        return "54" + phone[3:]
    return phone


# 2. Endpoint POST: Recepción de eventos y mensajes en tiempo real
@router.post("/webhook")
async def receive_webhook(payload: dict):
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
                
                # Comandos rápidos para invocar el menú
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
                    logger.info(f"Botón presionado: ID={selected_id}, Título='{button_title}'")
                    
                    # ==========================================
                    # RAMA 1: AGENDA DE TURNOS
                    # ==========================================
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
                            body_text="Seleccionaste Agenda de Turnos. ¿Qué deseas hacer?",
                            buttons=botones_turnos
                        )
                        
                    elif selected_id == "btn_turno_reservar":
                        user_state["estado"] = "RESERVANDO_TURNO"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        # Mostrar servicios y combos según tu flujo de Figma
                        secciones_servicios = [
                            {
                                "title": "Servicios Individuales",
                                "rows": [
                                    {"id": "srv_corte", "title": "Corte Masculino", "description": "Corte clásico o moderno - 30 min | $15.000"},
                                    {"id": "srv_barba", "title": "Perfilado de Barba", "description": "Arreglo con toalla caliente - 20 min | $8.000"}
                                ]
                            },
                            {
                                "title": "Combos Promocionales",
                                "rows": [
                                    {"id": "srv_combo_completo", "title": "Combo Estilo Completo", "description": "Corte + Barba + Toalla - 50 min | $20.000"},
                                    {"id": "srv_combo_color", "title": "Combo Coloración", "description": "Corte + Tintura Premium - 90 min | $32.000"}
                                ]
                            }
                        ]
                        await send_interactive_list(
                            phone=phone_number,
                            body_text="Por favor, selecciona el servicio individual o combo que deseas agendar:",
                            button_label="Ver Servicios 💇‍♀️",
                            sections=secciones_servicios,
                            header_text="Reserva de Turnos",
                            footer_text="Peluquería Estilo"
                        )
                    
                    elif selected_id in ["btn_turno_ver", "btn_turno_cancelar"]:
                        await send_message(
                            phone=phone_number,
                            text=f"Procesando opción '{button_title}'... Lógica en desarrollo para conectar con tu agenda real."
                        )
                        await clear_user_state(phone_number)
                        
                    # ==========================================
                    # RAMA 2: CATÁLOGO DE PRODUCTOS (Figma venta)
                    # ==========================================
                    elif selected_id == "btn_catalogo":
                        user_state["estado"] = "MENU_CATALOGO"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        # Productos físicos para reventa de peluquería
                        secciones_productos = [
                            {
                                "title": "Cuidado Capilar",
                                "rows": [
                                    {"id": "prod_shampoo", "title": "Shampoo Premium 300ml", "description": "Shampoo anticaída con ortiga | $3.500"},
                                    {"id": "prod_crema", "title": "Crema de Peinar", "description": "Modelado e hidratación profunda | $2.800"}
                                ]
                            },
                            {
                                "title": "Estilizado y Barba",
                                "rows": [
                                    {"id": "prod_cera", "title": "Cera Modeladora Matte", "description": "Fijación fuerte efecto seco | $3.200"},
                                    {"id": "prod_aceite", "title": "Aceite para Barba", "description": "Suaviza y nutre el vello facial | $3.000"}
                                ]
                            }
                        ]
                        await send_interactive_list(
                            phone=phone_number,
                            body_text="Bienvenido a nuestro catálogo de productos. Selecciona un producto para iniciar tu pedido:",
                            button_label="Ver Productos 🛍️",
                            sections=secciones_productos,
                            header_text="Productos de Venta",
                            footer_text="Peluquería Estilo"
                        )
                        
                    elif selected_id == "btn_prod_confirmar":
                        await send_message(
                            phone=phone_number,
                            text="✅ ¡Pedido registrado con éxito! Tu reserva de stock ha sido asentada. Puedes retirarlo por el local. ¡Gracias por tu compra!"
                        )
                        await clear_user_state(phone_number)
                        
                    elif selected_id == "btn_prod_volver":
                        # Limpiar estado y forzar el menú de productos nuevamente
                        user_state["estado"] = "MENU_PRINCIPAL"
                        await set_user_state(phone_number, user_state)
                        await send_message(phone=phone_number, text="Operación cancelada. Escribe 'Menú' para volver a empezar.")
                        
                    # ==========================================
                    # RAMA 3: PREGUNTAS FRECUENTES (FAQ)
                    # ==========================================
                    elif selected_id == "btn_faq":
                        user_state["estado"] = "ESPERANDO_FAQ"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        await send_message(
                            phone=phone_number,
                            text="Escribe tu consulta sobre la peluquería (Ej: horarios, dirección, métodos de pago)."
                        )
                        
                elif interactive_type == "list_reply":
                    reply = interactive_data.get("list_reply", {})
                    selected_id = reply.get("id")
                    row_title = reply.get("title", "")
                    logger.info(f"Opción de lista seleccionada por {phone_number}: ID={selected_id}, Título='{row_title}'")
                    
                    # Flujo de selección de servicio (Turnos)
                    if selected_id.startswith("srv_"):
                        user_state["estado"] = "ELIGE_FECHA"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        botones_fechas = [
                            {"id": "btn_fecha_hoy", "title": "Hoy"},
                            {"id": "btn_fecha_manana", "title": "Mañana"},
                            {"id": "btn_fecha_otro", "title": "Otro día"}
                        ]
                        await send_interactive_buttons(
                            phone=phone_number,
                            body_text=f"Elegiste: *{row_title}*.\n\nPor favor, selecciona qué día deseas agendar tu turno:",
                            buttons=botones_fechas
                        )
                        
                    # Flujo de selección de producto (Catálogo)
                    elif selected_id.startswith("prod_"):
                        user_state["estado"] = "CONFIRMA_PRODUCTO"
                        user_state["step"] += 1
                        await set_user_state(phone_number, user_state)
                        
                        # Botones para simular el check de stock y confirmación de compra
                        botones_confirmacion = [
                            {"id": "btn_prod_confirmar", "title": "🛒 Confirmar Pedido"},
                            {"id": "btn_prod_volver", "title": "🔄 Volver"}
                        ]
                        await send_interactive_buttons(
                            phone=phone_number,
                            body_text=f"Seleccionaste: *{row_title}*.\n\nContamos con stock disponible. ¿Deseas confirmar tu pedido para retiro presencial?",
                            buttons=botones_confirmacion
                        )
                        
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    return {"status": "success"}