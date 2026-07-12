import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Response, status
from app.core.settings import settings
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import get_user_state, set_user_state, clear_user_state
from app.services.event_logger import log_event

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# CONSTANTES DE CONFIGURACIÓN (ÁRBOL DE NAVEGACIÓN ESTÁTICO)
# =============================================================================
# TODO: Resolver business_id desde el phone_number_id del webhook de Meta.
# Mientras tanto se usa un valor fijo para desarrollo.
MOCK_BUSINESS_ID = 1
BOTONES_PRINCIPALES = [
    {"id": "btn_turnos", "title": "📅 Turnos"},
    {"id": "btn_catalogo", "title": "🛍️ Catálogo"},
    {"id": "btn_faq", "title": "❓ FAQ"}
]

BOTONES_TURNOS = [
    {"id": "btn_turno_reservar", "title": "➕ Reservar"},
    {"id": "btn_turno_ver", "title": "👀 Ver próximo"},
    {"id": "btn_turno_cancelar", "title": "❌ Cancelar"}
]

SECCIONES_SERVICIOS = [
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

SECCIONES_PRODUCTOS = [
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


# =============================================================================
# MANEJADORES DE ESTADO (HANDLERS)
# =============================================================================

async def handle_welcome_flow(phone: str):
    """Envia el mensaje de bienvenida y el menú de botones principal (Criterio 1)."""
    await clear_user_state(phone)
    initial_state = {"estado": "MENU_PRINCIPAL", "step": 1}
    await set_user_state(phone, initial_state)

    # Evento: conversation_started
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="conversation_started",
        payload={"is_new_user": True, "channel": "whatsapp"},
    )
    
    await send_interactive_buttons(
        phone=phone,
        body_text="¡Hola! Bienvenido a la Peluquería Estilo. ¿En qué podemos ayudarte hoy?",
        buttons=BOTONES_PRINCIPALES
    )

async def handle_text_fallback(phone: str, user_text: str, user_state: dict):
    """
    Manejador de Fallback para capturar texto libre no transaccional (Criterio 3).
    Prepara la interfaz para la posterior conexión con LLM y servidores MCP.
    """
    logger.info(f"Enrutamiento de Fallback activado. Entrada: '{user_text}'. Estado: {user_state}")

    fallback_n = user_state.get("fallback_count", 0) + 1
    user_state["fallback_count"] = fallback_n

    # Evento: fallback_triggered
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="fallback_triggered",
        payload={
            "message_original": user_text,
            "previous_state": user_state.get("estado"),
            "fallback_n": fallback_n,
        },
    )

    # Escalamiento a humano tras 2 fallbacks consecutivos
    if fallback_n >= 2:
        user_state["estado"] = "HUMAN_ESCALATION"
        await set_user_state(phone, user_state)
        # Evento: escalation_to_human
        log_event(
            session_id=phone,
            business_id=MOCK_BUSINESS_ID,
            event_type="escalation_to_human",
            payload={
                "reason": "fallback_exceeded",
                "n_fallbacks_previos": fallback_n,
                "current_flow_state": user_state.get("estado"),
            },
        )
        await send_message(
            phone=phone,
            text="Estamos teniendo dificultades para entenderte. Un representante humano se pondrá en contacto contigo pronto.",
        )
        return
    
    fallback_message = (
        "Por ahora soy un bot básico, pronto usaré IA para responder esto 🧠.\n\n"
        "Por favor, selecciona una de las opciones del menú interactivo para continuar. "
        "Si deseas volver al inicio, escribe *Menú*."
    )
    await send_message(phone=phone, text=fallback_message)

async def handle_main_menu_selection(phone: str, button_id: str, user_state: dict):
    """Procesa las interacciones del Menú Principal."""
    # Evento: menu_option_selected
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="menu_option_selected",
        payload={"option_name": button_id},
    )

    if button_id == "btn_turnos":
        user_state["estado"] = "MENU_TURNOS"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_interactive_buttons(
            phone=phone,
            body_text="Seleccionaste Agenda de Turnos. ¿Qué deseas hacer?",
            buttons=BOTONES_TURNOS
        )
        
    elif button_id == "btn_catalogo":
        user_state["estado"] = "MENU_CATALOGO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_interactive_list(
            phone=phone,
            body_text="Bienvenido a nuestro catálogo de productos. Selecciona un producto para iniciar tu pedido:",
            button_label="Ver Productos 🛍️",
            sections=SECCIONES_PRODUCTOS,
            header_text="Productos de Venta",
            footer_text="Peluquería Estilo"
        )
        
    elif button_id == "btn_faq":
        user_state["estado"] = "ESPERANDO_FAQ"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_message(
            phone=phone,
            text="Escribe tu consulta sobre la peluquería (Ej: horarios, dirección, métodos de pago)."
        )

async def handle_turnos_menu_selection(phone: str, button_id: str, user_state: dict):
    """Procesa el árbol transaccional de la agenda de turnos."""
    if button_id == "btn_turno_reservar":
        user_state["estado"] = "RESERVANDO_TURNO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_interactive_list(
            phone=phone,
            body_text="Por favor, selecciona el servicio individual o combo que deseas agendar:",
            button_label="Ver Servicios 💇‍♀️",
            sections=SECCIONES_SERVICIOS,
            header_text="Reserva de Turnos",
            footer_text="Peluquería Estilo"
        )
    elif button_id in ["btn_turno_ver", "btn_turno_cancelar"]:
        action_title = "Ver Turno" if button_id == "btn_turno_ver" else "Cancelar Turno"
        await send_message(
            phone=phone,
            text=f"Procesando opción '{action_title}'... Lógica en desarrollo para conectar con tu agenda real."
        )
        # Evento: conversation_closed
        log_event(
            session_id=phone,
            business_id=MOCK_BUSINESS_ID,
            event_type="conversation_closed",
            payload={"resultado_final": "turno_consulta", "n_fallbacks": user_state.get("fallback_count", 0)},
        )
        await clear_user_state(phone)

async def handle_catalogo_menu_selection(phone: str, button_id: str, user_state: dict):
    """Maneja la confirmación de la reserva de productos físicos."""
    if button_id == "btn_prod_confirmar":
        await send_message(
            phone=phone,
            text="✅ ¡Pedido registrado con éxito! Tu reserva de stock ha sido asentada. Puedes retirarlo por el local. ¡Gracias por tu compra!"
        )
        # Evento: conversation_closed
        log_event(
            session_id=phone,
            business_id=MOCK_BUSINESS_ID,
            event_type="conversation_closed",
            payload={"resultado_final": "producto_comprado", "n_fallbacks": user_state.get("fallback_count", 0)},
        )
        await clear_user_state(phone)
    elif button_id == "btn_prod_volver":
        await handle_welcome_flow(phone)

async def handle_date_selection(phone: str, button_title: str, user_state: dict):
    """Guarda la fecha seleccionada por botón y solicita el horario."""
    user_state["estado"] = "ELIGE_HORARIO"
    user_state["step"] += 1
    user_state["fecha_seleccionada"] = button_title
    await set_user_state(phone, user_state)
    
    botones_horarios = [
        {"id": "btn_hora_10", "title": "10:00 hs"},
        {"id": "btn_hora_15", "title": "15:00 hs"},
        {"id": "btn_hora_18", "title": "18:00 hs"}
    ]
    await send_interactive_buttons(
        phone=phone,
        body_text=f"Elegiste: *{button_title}*.\n\nPor favor, selecciona uno de nuestros horarios disponibles para tu cita:",
        buttons=botones_horarios
    )

async def handle_time_selection(phone: str, button_title: str, user_state: dict):
    """Guarda la hora seleccionada por botón y solicita el nombre por teclado."""
    user_state["estado"] = "ESPERANDO_NOMBRE"
    user_state["step"] += 1
    user_state["hora_seleccionada"] = button_title
    await set_user_state(phone, user_state)
    
    await send_message(
        phone=phone,
        text=f"Elegiste las *{button_title}*.\n\nPara finalizar el registro, por favor **escribe tu Nombre y Apellido** por teclado:"
    )

async def handle_appointment_confirmation(phone: str, user_text: str, user_state: dict):
    """Confirma el agendamiento del turno con los parámetros consolidados."""
    fecha = user_state.get("fecha_seleccionada", "Hoy")
    hora = user_state.get("hora_seleccionada", "10:00 hs")
    servicio = user_state.get("servicio_seleccionado", "Combo Estilo Completo")

    # Evento: appointment_created
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="appointment_created",
        payload={"via_bot": True, "servicio": servicio, "fecha": fecha, "hora": hora},
    )
    # Evento: reminder_sent (placeholder — se registra intención de recordatorio futuro)
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="reminder_sent",
        payload={"servicio": servicio, "fecha": fecha, "hora": hora},
    )
    
    confirmacion_text = (
        f"🎉 *¡Turno Agendado con Éxito!*\n\n"
        f"👤 *Cliente:* {user_text}\n"
        f"💇‍♀️ *Servicio:* {servicio}\n"
        f"📅 *Día:* {fecha}\n"
        f"⏰ *Hora:* {hora}\n\n"
        f"Te enviaremos un recordatorio antes de tu cita. ¡Muchas gracias por elegirnos! 💇‍♀️✨"
    )
    await send_message(phone=phone, text=confirmacion_text)
    # Evento: conversation_closed
    log_event(
        session_id=phone,
        business_id=MOCK_BUSINESS_ID,
        event_type="conversation_closed",
        payload={"resultado_final": "turno_creado", "n_fallbacks": user_state.get("fallback_count", 0)},
    )
    await clear_user_state(phone)

async def handle_list_selection(phone: str, selected_id: str, row_title: str, user_state: dict):
    """Maneja las selecciones efectuadas en los menús de tipo lista desplegable."""
    if selected_id.startswith("srv_"):
        # Evento: service_selected
        log_event(
            session_id=phone,
            business_id=MOCK_BUSINESS_ID,
            event_type="service_selected",
            payload={"service_id": selected_id, "service_name": row_title},
        )

        user_state["estado"] = "ELIGE_FECHA"
        user_state["step"] += 1
        user_state["servicio_seleccionado"] = row_title
        await set_user_state(phone, user_state)
        
        botones_fechas = [
            {"id": "btn_fecha_hoy", "title": "Hoy"},
            {"id": "btn_fecha_manana", "title": "Mañana"},
            {"id": "btn_fecha_otro", "title": "Otro día"}
        ]
        await send_interactive_buttons(
            phone=phone,
            body_text=f"Elegiste: *{row_title}*.\n\nPor favor, selecciona qué día deseas agendar tu turno:",
            buttons=botones_fechas
        )
        
    elif selected_id.startswith("prod_"):
        user_state["estado"] = "CONFIRMA_PRODUCTO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        botones_confirmacion = [
            {"id": "btn_prod_confirmar", "title": "🛒 Confirmar Pedido"},
            {"id": "btn_prod_volver", "title": "🔄 Volver"}
        ]
        await send_interactive_buttons(
            phone=phone,
            body_text=f"Seleccionaste: *{row_title}*.\n\nContamos con stock disponible. ¿Deseas confirmar tu pedido para retiro presencial?",
            buttons=botones_confirmacion
        )


# =============================================================================
# ENRUTADOR ASÍNCRONO DEL WEBHOOK (STATE ROUTER)
# =============================================================================

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


# 2. Endpoint POST: Recepción y Enrutamiento asíncrono de Eventos
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
            # Saneamiento del número telefónico de origen
            # --- SANITIZACIÓN DE TELÉFONO ANTES DE INTERACTUAR CON EL ESTADO ---
            # TODO: Remover este bloque al pasar a Producción con número real.
            if settings.APP_ENV == "development" and phone_number.startswith("549"):
                area_code = phone_number[3:5] 
                local_number = phone_number[5:]
                phone_number = f"54{area_code}15{local_number}"
                logger.info(f"Aplicado parche Sandbox Argentina: {phone_number}")
            else:
                phone_number = clean_phone_number(phone_number)
            
            # Consultar o inicializar estado conversacional de Redis
            user_state = await get_user_state(phone_number)
            current_step = user_state.get("estado") if user_state else "NUEVO"
            
            # --- CASO A: MENSAJES DE TEXTO PLANO ---
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()
                logger.info(f"Mensaje de texto de {phone_number}: '{user_text}'")
                
                # Comandos de reinicio explícito o inicialización por defecto (Criterio 1)
                if user_text.lower() in ["hola", "menu", "menú", "volver", "comenzar", "salir"] or current_step == "NUEVO":
                    await handle_welcome_flow(phone_number)
                
                # Captura del nombre del usuario (Fin del árbol transaccional)
                elif current_step == "ESPERANDO_NOMBRE":
                    await handle_appointment_confirmation(phone_number, user_text, user_state)

                # Respuesta a recordatorio de turno (SI / NO / CANCELAR / CONFIRMO / CANCELO / CAMBIO)
                elif user_text.upper() in ["SI", "NO", "CANCELAR", "CONFIRMO", "CANCELO", "CAMBIO"]:
                    response_map = {
                        "SI": "confirmo", "CONFIRMO": "confirmo",
                        "NO": "cancelo", "CANCELAR": "cancelo", "CANCELO": "cancelo",
                        "CAMBIO": "cambio",
                    }
                    response_type = response_map.get(user_text.upper(), "desconocido")
                    log_event(
                        session_id=phone_number,
                        business_id=MOCK_BUSINESS_ID,
                        event_type="reminder_response",
                        payload={"response_type": response_type, "raw_text": user_text},
                    )
                    await send_message(
                        phone=phone_number,
                        text="¡Gracias por tu respuesta! La hemos registrado.",
                    )
                    await handle_welcome_flow(phone_number)

                # Puntaje de satisfacción (CSAT): número 1-5 como mensaje independiente
                elif user_text.strip().isdigit() and 1 <= int(user_text.strip()) <= 5:
                    score = int(user_text.strip())
                    outcome = "turno_exitoso"
                    if user_state and user_state.get("estado") == "HUMAN_ESCALATION":
                        outcome = "escalado_exitoso"

                    # Escribir en tabla event (trazabilidad existente)
                    log_event(
                        session_id=phone_number,
                        business_id=MOCK_BUSINESS_ID,
                        event_type="csat_submitted",
                        payload={"score": score, "outcome": outcome},
                    )

                    # Escribir en tabla feedback (fuente canónica de métricas — FR-E2)
                    from app.db.database import SessionLocal
                    from app.db.models.feedback import Feedback
                    from datetime import timezone

                    db_fb = SessionLocal()
                    try:
                        fb = Feedback(
                            business_id=MOCK_BUSINESS_ID,
                            session_id=phone_number,
                            score=score,
                            outcome=outcome,
                            user_phone=phone_number,
                            submitted_at=datetime.now(timezone.utc),
                        )
                        db_fb.add(fb)
                        db_fb.commit()
                        logger.info(f"CSAT guardado en feedback: score={score}, outcome={outcome}")
                    except Exception:
                        db_fb.rollback()
                        logger.exception("Error guardando CSAT en tabla feedback")
                    finally:
                        db_fb.close()

                    await send_message(
                        phone=phone_number,
                        text=f"¡Gracias por tu calificación de {score} estrellas! ⭐",
                    )
                    await handle_welcome_flow(phone_number)

                # Enrutamiento al Fallback Híbrido para textos no estructurados (Criterio 3)
                else:
                    await handle_text_fallback(phone_number, user_text, user_state)
                    
            # --- CASO B: RESPUESTAS INTERACTIVAS (BOTONES Y LISTAS) ---
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")
                
                if interactive_type == "button_reply":
                    reply = interactive_data.get("button_reply", {})
                    selected_id = reply.get("id")
                    button_title = reply.get("title", "")
                    logger.info(f"Botón presionado: ID={selected_id}, Título='{button_title}'")
                    
                    # Enrutamiento basado en la máquina de estados (Criterio 4)
                    if current_step == "MENU_PRINCIPAL":
                        await handle_main_menu_selection(phone_number, selected_id, user_state)
                        
                    elif current_step == "MENU_TURNOS":
                        await handle_turnos_menu_selection(phone_number, selected_id, user_state)
                        
                    elif current_step == "CONFIRMA_PRODUCTO":
                        await handle_catalogo_menu_selection(phone_number, selected_id, user_state)
                        
                    elif current_step == "ELIGE_FECHA" and selected_id.startswith("btn_fecha_"):
                        await handle_date_selection(phone_number, button_title, user_state)
                        
                    elif current_step == "ELIGE_HORARIO" and selected_id.startswith("btn_hora_"):
                        await handle_time_selection(phone_number, button_title, user_state)
                        
                    else:
                        # Fallback de seguridad ante estados desincronizados: re-enviar bienvenida
                        await handle_welcome_flow(phone_number)
                        
                elif interactive_type == "list_reply":
                    reply = interactive_data.get("list_reply", {})
                    selected_id = reply.get("id")
                    row_title = reply.get("title", "")
                    logger.info(f"Opción de lista seleccionada por {phone_number}: ID={selected_id}, Título='{row_title}'")
                    
                    await handle_list_selection(phone_number, selected_id, row_title, user_state)
                    
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    return {"status": "success"}