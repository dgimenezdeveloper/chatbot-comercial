import logging
import zoneinfo
from datetime import datetime, date, timedelta, timezone

from fastapi import APIRouter, Query, Response, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import get_db
from app.db.models.sessions import ChatSession
from app.db.models.feedback import Feedback
from app.db.models.service import Service
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import get_user_state, set_user_state, clear_user_state
from app.services.event_logger import log_event
from app.services.negocio import get_active_services, get_available_slots, get_business_timezone
from app.services.catalog import get_products
from app.services.calendar import create_appointment, get_appointments_by_phone, cancel_appointment
from app.services.faq import search_faqs, get_faqs

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# CONSTANTES DE CONFIGURACIÓN (MENÚS BASE)
# =============================================================================
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


# =============================================================================
# HELPER DE CAMBIO DE TENANT PARA LA DEMO
# =============================================================================

async def _reset_demo_tenant(db: Session, phone_number: str, target_business_id: int, business_name: str):
    """Actualiza el business_id de la sesión en PostgreSQL y limpia el estado en Redis."""
    variants = {phone_number}
    if phone_number.startswith("541115"):
        variants.add("54911" + phone_number[6:])
    elif phone_number.startswith("54911"):
        variants.add("541115" + phone_number[5:])
    
    sessions = db.query(ChatSession).filter(
        or_(
            ChatSession.session_id.in_(variants),
            ChatSession.user_phone.in_(variants)
        )
    ).all()
    
    if sessions:
        for s in sessions:
            s.business_id = target_business_id
        db.commit()
        logger.info(f"Demo cambiada a {business_name} (ID {target_business_id}) para {len(sessions)} sesion(es)")
    else:
        new_s = ChatSession(
            session_id=phone_number,
            business_id=target_business_id,
            user_phone=phone_number,
            status="active"
        )
        db.add(new_s)
        db.commit()

    for v in variants:
        await clear_user_state(v)

    await send_message(
        phone=phone_number,
        text=f"✅ Demo cambiada con éxito. Ahora estás interactuando con la {business_name} (ID {target_business_id})."
    )


# =============================================================================
# MANEJADORES DE ESTADO (HANDLERS DINÁMICOS)
# =============================================================================

async def handle_welcome_flow(phone: str, business_id: int, db: Session):
    """Envia el mensaje de bienvenida y el menú de botones principal."""
    await clear_user_state(phone)
    initial_state = {"estado": "MENU_PRINCIPAL", "step": 1}
    await set_user_state(phone, initial_state)

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="conversation_started",
        payload={"is_new_user": True, "channel": "whatsapp"},
    )
    
    nombre_negocio = "Peluquería Estilo" if business_id == 1 else "Barbería Innova"
    
    await send_interactive_buttons(
        phone=phone,
        body_text=f"¡Hola! Bienvenido a {nombre_negocio}. ¿En qué podemos ayudarte hoy?",
        buttons=BOTONES_PRINCIPALES
    )


async def handle_text_fallback(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    """Manejador de Fallback para texto libre no estructurado."""
    logger.info(f"Enrutamiento de Fallback activado. Entrada: '{user_text}'. Estado: {user_state}")

    fallback_n = user_state.get("fallback_count", 0) + 1
    user_state["fallback_count"] = fallback_n

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="fallback_triggered",
        payload={
            "message_original": user_text,
            "previous_state": user_state.get("estado"),
            "fallback_n": fallback_n,
        },
    )

    if fallback_n >= 2:
        user_state["estado"] = "HUMAN_ESCALATION"
        await set_user_state(phone, user_state)
        
        log_event(
            session_id=phone,
            business_id=business_id,
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


async def handle_main_menu_selection(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    """Procesa las interacciones del Menú Principal con datos dinámicos."""
    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="menu_option_selected",
        payload={"option_name": button_id},
    )

    nombre_negocio = "Peluquería Estilo" if business_id == 1 else "Barbería Innova"

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
        products = get_products(db, business_id)
        if not products:
            await send_message(
                phone=phone,
                text=f"🛒 {nombre_negocio} aún no tiene productos registrados en su catálogo de venta directa."
            )
            return

        rows = []
        for p in products[:10]:
            rows.append({
                "id": f"prod_{p.id}",
                "title": p.name[:24],
                "description": f"Stock: {p.stock_quantity or 0} | ${float(p.price):,.0f}"[:72]
            })

        sections = [{"title": "Productos Disponibles"[:20], "rows": rows}]

        user_state["estado"] = "MENU_CATALOGO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_interactive_list(
            phone=phone,
            body_text="Bienvenido a nuestro catálogo. Selecciona un producto para reservar tu pedido:",
            button_label="Ver Productos 🛍️",
            sections=sections,
            header_text="Productos de Venta",
            footer_text=nombre_negocio
        )
        
    elif button_id == "btn_faq":
        user_state["estado"] = "ESPERANDO_FAQ"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_message(
            phone=phone,
            text="Escribe tu consulta sobre el local (Ej: horarios, dirección, métodos de pago, o la pregunta que tengas)."
        )


async def handle_turnos_menu_selection(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    """Procesa la reserva o la consulta/cancelación de turnos."""
    nombre_negocio = "Peluquería Estilo" if business_id == 1 else "Barbería Innova"

    if button_id == "btn_turno_reservar":
        services = get_active_services(db, business_id)
        if not services:
            await send_message(
                phone=phone,
                text=f"💇‍♀️ {nombre_negocio} actualmente no tiene servicios activos configurados en su agenda."
            )
            return

        categories = {}
        for s in services[:10]:
            cat_name = s.category.value if hasattr(s.category, 'value') else str(s.category)
            cat_title = cat_name.capitalize()[:20]
            if cat_title not in categories:
                categories[cat_title] = []
            
            categories[cat_title].append({
                "id": f"srv_{s.id}",
                "title": s.name[:24],
                "description": f"{s.duration_minutes or 30} min | ${float(s.price):,.0f}"[:72]
            })

        sections = [{"title": title, "rows": rows} for title, rows in categories.items()]

        user_state["estado"] = "RESERVANDO_TURNO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        
        await send_interactive_list(
            phone=phone,
            body_text="Por favor, selecciona el servicio que deseas agendar:",
            button_label="Ver Servicios 💇‍♀️",
            sections=sections,
            header_text="Reserva de Turnos",
            footer_text=nombre_negocio
        )

    elif button_id == "btn_turno_ver":
        await handle_view_appointment(phone, user_state, business_id, db)

    elif button_id == "btn_turno_cancelar":
        await handle_cancel_appointment_flow(phone, user_state, business_id, db)


# =============================================================================
# MANEJADORES DE CONSULTA / CANCELACIÓN DE TURNOS
# =============================================================================

async def handle_view_appointment(phone: str, user_state: dict, business_id: int, db: Session):
    """Consulta en la base de datos el próximo turno activo del cliente."""
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    
    # Filtrar turnos activos futuros
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]
    
    if not upcoming:
        await send_message(
            phone=phone,
            text="👀 No encontramos turnos próximos agendados para tu número de teléfono."
        )
    else:
        next_appt = upcoming[0]
        service = db.query(Service).filter(Service.id == next_appt.service_id).first()
        svc_name = service.name if service else "Servicio General"
        
        tz_str = get_business_timezone(db, business_id)
        local_dt = next_appt.scheduled_date.astimezone(zoneinfo.ZoneInfo(tz_str))
        
        msg = (
            f"👀 *Tu próximo turno agendado:*\n\n"
            f"👤 *Cliente:* {next_appt.user_name or 'Registrado'}\n"
            f"💇‍♀️ *Servicio:* {svc_name}\n"
            f"📅 *Fecha:* {local_dt.strftime('%d/%m/%Y')}\n"
            f"⏰ *Hora:* {local_dt.strftime('%H:%M')} hs\n"
            f"📌 *Estado:* {next_appt.status.capitalize()}\n\n"
            f"Si deseas realizar un nuevo agendamiento o cancelar, escribe *Menú*."
        )
        await send_message(phone=phone, text=msg)

    await clear_user_state(phone)


async def handle_cancel_appointment_flow(phone: str, user_state: dict, business_id: int, db: Session):
    """Inicia el flujo para cancelar turnos activos."""
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]
    
    if not upcoming:
        await send_message(
            phone=phone,
            text="❌ No tienes turnos activos próximos para cancelar."
        )
        await clear_user_state(phone)
        return

    tz_str = get_business_timezone(db, business_id)

    if len(upcoming) == 1:
        appt = upcoming[0]
        service = db.query(Service).filter(Service.id == appt.service_id).first()
        svc_name = service.name if service else "Servicio"
        local_dt = appt.scheduled_date.astimezone(zoneinfo.ZoneInfo(tz_str))
        
        user_state["estado"] = "CONFIRMA_CANCELACION"
        await set_user_state(phone, user_state)
        
        buttons = [
            {"id": f"btn_confirm_cancel_{appt.id}", "title": "SÍ, Cancelar ❌"},
            {"id": "btn_cancel_abort", "title": "NO, Volver 🔙"}
        ]
        await send_interactive_buttons(
            phone=phone,
            body_text=(
                f"⚠️ *¿Estás seguro de cancelar este turno?*\n\n"
                f"💇‍♀️ *Servicio:* {svc_name}\n"
                f"📅 *Fecha:* {local_dt.strftime('%d/%m/%Y')} a las {local_dt.strftime('%H:%M')} hs"
            ),
            buttons=buttons
        )
    else:
        # Si tiene múltiples turnos, listamos
        rows = []
        for appt in upcoming[:10]:
            service = db.query(Service).filter(Service.id == appt.service_id).first()
            svc_name = service.name if service else "Servicio"
            local_dt = appt.scheduled_date.astimezone(zoneinfo.ZoneInfo(tz_str))
            rows.append({
                "id": f"cancel_appt_{appt.id}",
                "title": f"{svc_name}"[:24],
                "description": f"{local_dt.strftime('%d/%m %H:%M hs')}"[:72]
            })
        
        user_state["estado"] = "SELECCIONA_TURNO_CANCELAR"
        await set_user_state(phone, user_state)
        
        sections = [{"title": "Turnos Activos"[:20], "rows": rows}]
        await send_interactive_list(
            phone=phone,
            body_text="Tienes varios turnos agendados. Por favor selecciona cuál deseas cancelar:",
            button_label="Ver Turnos 📋",
            sections=sections
        )


async def handle_cancel_confirmation(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    """Procesa la cancelación definitiva del turno en PostgreSQL y Google Calendar."""
    if button_id.startswith("btn_confirm_cancel_"):
        try:
            appt_id = int(button_id.replace("btn_confirm_cancel_", ""))
        except ValueError:
            await send_message(phone, "Error al procesar la cancelación.")
            await clear_user_state(phone)
            return

        canceled_appt = cancel_appointment(
            db=db,
            appointment_id=appt_id,
            business_id=business_id,
            reason="Cancelado por el cliente vía WhatsApp"
        )
        
        if canceled_appt:
            log_event(
                session_id=phone,
                business_id=business_id,
                event_type="appointment_cancelled",
                payload={"appointment_id": appt_id, "reason": "cancelado_por_cliente"},
            )
            await send_message(
                phone=phone,
                text="✅ Tu turno ha sido cancelado con éxito. El horario ha sido liberado en nuestra agenda y en el calendario."
            )
        else:
            await send_message(
                phone=phone,
                text="⚠️ Ocurrió un inconveniente al cancelar el turno. Puede que ya estuviera cancelado previamente."
            )
        await clear_user_state(phone)

    elif button_id == "btn_cancel_abort":
        await send_message(phone=phone, text="👍 Entendido, conservamos tu turno agendado sin cambios.")
        await handle_welcome_flow(phone, business_id, db)


# =============================================================================
# MANEJADOR DE PREGUNTAS FRECUENTES (FAQ)
# =============================================================================

async def handle_faq_query(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    """Busca respuestas en la base de datos de preguntas frecuentes."""
    faqs_encontradas = search_faqs(db, business_id, user_text)
    
    if faqs_encontradas:
        faq = faqs_encontradas[0]
        respuesta_text = f"❓ *Pregunta:* {faq.question}\n\n💡 *Respuesta:* {faq.answer}"
        await send_message(phone=phone, text=respuesta_text)
        
        log_event(
            session_id=phone,
            business_id=business_id,
            event_type="faq_answered",
            payload={"faq_id": faq.id, "query": user_text},
        )
    else:
        # Si no hay coincidencia directa, mostramos las 3 principales FAQs del local
        todas_faqs = get_faqs(db, business_id)
        if todas_faqs:
            msg = "No encontré una respuesta exacta para tu consulta, pero aquí tienes algunas preguntas frecuentes:\n\n"
            for f in todas_faqs[:3]:
                msg += f"• *{f.question}*\n  {f.answer}\n\n"
            await send_message(phone=phone, text=msg)
        else:
            await send_message(
                phone=phone,
                text="No encontramos respuestas para tu consulta en este momento. Por favor, escribe *Menú* para ver más opciones."
            )
            
    await handle_welcome_flow(phone, business_id, db)


# =============================================================================
# OTROS MANEJADORES EXISTENTES
# =============================================================================

async def handle_catalogo_menu_selection(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    """Maneja la confirmación de pedido de productos."""
    if button_id == "btn_prod_confirmar":
        await send_message(
            phone=phone,
            text="✅ ¡Pedido registrado con éxito! Tu reserva de stock ha sido asentada. Puedes retirarlo por el local. ¡Gracias por tu compra!"
        )
        log_event(
            session_id=phone,
            business_id=business_id,
            event_type="conversation_closed",
            payload={"resultado_final": "producto_comprado", "n_fallbacks": user_state.get("fallback_count", 0)},
        )
        await clear_user_state(phone)
    elif button_id == "btn_prod_volver":
        await handle_welcome_flow(phone, business_id, db)


async def handle_date_selection(phone: str, button_title: str, user_state: dict, business_id: int, db: Session):
    """Calcula slots libres reales en DB usando la duración del servicio seleccionado."""
    today = date.today()
    if button_title.lower() == "hoy":
        target_date = today
    elif button_title.lower() in ["mañana", "manana"]:
        target_date = today + timedelta(days=1)
    else:
        target_date = today + timedelta(days=2)

    user_state["estado"] = "ELIGE_HORARIO"
    user_state["step"] += 1
    user_state["fecha_seleccionada"] = button_title
    user_state["fecha_iso"] = target_date.isoformat()
    await set_user_state(phone, user_state)
    
    service_id = user_state.get("servicio_id")
    if not service_id:
        active_svcs = get_active_services(db, business_id)
        if active_svcs:
            service_id = active_svcs[0].id
        else:
            await send_message(phone=phone, text="Error: No hay servicios disponibles para esta fecha.")
            return

    available_slots = get_available_slots(db, service_id, business_id, target_date)

    if not available_slots:
        await send_message(
            phone=phone,
            text=f"Lo sentimos, no hay horarios disponibles para el día *{button_title}*. Por favor, intenta elegir otra fecha."
        )
        return

    botones_horarios = []
    for slot in available_slots[:3]:
        hora_str = slot.strftime("%H:%M")
        botones_horarios.append({
            "id": f"btn_hora_{slot.strftime('%H%M')}",
            "title": f"{hora_str} hs"
        })

    await send_interactive_buttons(
        phone=phone,
        body_text=f"Elegiste: *{button_title}*.\n\nHorarios disponibles encontrados en agenda:",
        buttons=botones_horarios
    )


async def handle_time_selection(phone: str, button_title: str, user_state: dict, business_id: int, db: Session):
    """Guarda la hora seleccionada y solicita el nombre del cliente."""
    user_state["estado"] = "ESPERANDO_NOMBRE"
    user_state["step"] += 1
    user_state["hora_seleccionada"] = button_title
    await set_user_state(phone, user_state)
    
    await send_message(
        phone=phone,
        text=f"Elegiste las *{button_title}*.\n\nPara finalizar el registro, por favor **escribe tu Nombre y Apellido** por teclado:"
    )


async def handle_appointment_confirmation(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    """Confirma el agendamiento del turno, guarda/actualiza el Cliente y persiste en DB."""
    fecha_label = user_state.get("fecha_seleccionada", "Hoy")
    fecha_iso = user_state.get("fecha_iso", date.today().isoformat())
    hora_label = user_state.get("hora_seleccionada", "10:00 hs")
    servicio_nombre = user_state.get("servicio_seleccionado", "Servicio General")
    servicio_id = user_state.get("servicio_id")

    if not servicio_id:
        active_svcs = get_active_services(db, business_id)
        servicio_id = active_svcs[0].id if active_svcs else 1

    time_part = hora_label.replace(" hs", "").strip()
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)
    
    dt_str = f"{fecha_iso} {time_part}"
    scheduled_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    # 1. Guardar/Actualizar el Cliente en la tabla 'user' para el Dashboard de Clientes
    user = get_or_create_user(db, phone, business_id, name=user_text.strip())
    if user and user_text.strip() and user.name != user_text.strip():
        user.name = user_text.strip()
        db.commit()

    # 2. Datos del Turno
    appt_data = {
        "business_id": business_id,
        "user_id": user.id if user else None, # 👈 Vinculación directa con el Cliente
        "user_phone": phone,
        "user_name": user_text[:200],
        "service_id": servicio_id,
        "scheduled_date": scheduled_date,
        "status": "confirmed",
        "created_via": "chatbot",
        "session_id": phone
    }
    
    try:
        appointment = create_appointment(db, appt_data)
        appt_id = appointment.id
        logger.info(f"Turno guardado en DB exitosamente: ID {appt_id}")
    except Exception as e:
        logger.error(f"Error al guardar el turno en DB: {e}")
        await send_message(phone, "Hubo un error interno al guardar tu turno. Por favor, intenta nuevamente más tarde.")
        await clear_user_state(phone)
        return

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="appointment_created",
        payload={"appointment_id": appt_id, "via_bot": True, "servicio": servicio_nombre, "fecha": fecha_iso, "hora": time_part},
    )
    
    confirmacion_text = (
        f"🎉 *¡Turno Agendado con Éxito!*\n\n"
        f"👤 *Cliente:* {user_text}\n"
        f"💇‍♀️ *Servicio:* {servicio_nombre}\n"
        f"📅 *Día:* {fecha_label}\n"
        f"⏰ *Hora:* {hora_label}\n\n"
        f"Te enviaremos un recordatorio antes de tu cita. ¡Muchas gracias por elegirnos! 💇‍♀️✨"
    )
    await send_message(phone=phone, text=confirmacion_text)
    
    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="conversation_closed",
        payload={"resultado_final": "turno_creado", "n_fallbacks": user_state.get("fallback_count", 0)},
    )
    await clear_user_state(phone)

async def handle_list_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Maneja las selecciones efectuadas en los menús de tipo lista desplegable."""
    if selected_id.startswith("srv_"):
        try:
            svc_db_id = int(selected_id.replace("srv_", ""))
        except ValueError:
            svc_db_id = 1

        log_event(
            session_id=phone,
            business_id=business_id,
            event_type="service_selected",
            payload={"service_id": svc_db_id, "service_name": row_title},
        )

        user_state["estado"] = "ELIGE_FECHA"
        user_state["step"] += 1
        user_state["servicio_id"] = svc_db_id
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
    if phone.startswith("54911"):
        return "541115" + phone[5:]
    return phone


@router.post("/webhook")
async def receive_webhook(payload: dict, db: Session = Depends(get_db)):
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
            
            # Sanitización de teléfono
            if settings.APP_ENV == "development" and phone_number.startswith("549"):
                area_code = phone_number[3:5] 
                local_number = phone_number[5:]
                phone_number = f"54{area_code}15{local_number}"
                logger.info(f"Aplicado parche Sandbox Argentina: {phone_number}")
            else:
                phone_number = clean_phone_number(phone_number)
            
            # --- GESTIÓN DE SESIÓN EN POSTGRESQL ---
            db_session = db.query(ChatSession).filter(ChatSession.session_id == phone_number).first()
            if not db_session:
                db_session = ChatSession(
                    session_id=phone_number,
                    business_id=MOCK_BUSINESS_ID,
                    user_phone=phone_number,
                    status="active"
                )
                db.add(db_session)
                db.commit()
                db.refresh(db_session)
                logger.info(f"Nueva sesión creada en DB para {phone_number} (Business ID: {db_session.business_id})")

            current_business_id = db_session.business_id

            # Estado conversacional en Redis
            user_state = await get_user_state(phone_number)
            current_step = user_state.get("estado") if user_state else "NUEVO"
            
            # --- CASO A: MENSAJES DE TEXTO PLANO ---
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()
                logger.info(f"Mensaje de texto de {phone_number}: '{user_text}'")
                
                # --- COMANDO SECRETO PARA DEMO EN VIVO ---
                if user_text.lower() == "/reset_demo estetica":
                    await _reset_demo_tenant(db, phone_number, 1, "Peluquería")
                    return {"status": "success"}
                
                elif user_text.lower() == "/reset_demo barberia":
                    await _reset_demo_tenant(db, phone_number, 2, "Barbería")
                    return {"status": "success"}

                if user_text.lower() in ["hola", "menu", "menú", "volver", "comenzar", "salir"] or current_step == "NUEVO":
                    await handle_welcome_flow(phone_number, current_business_id, db)
                
                elif current_step == "ESPERANDO_NOMBRE":
                    await handle_appointment_confirmation(phone_number, user_text, user_state, current_business_id, db)

                elif current_step == "ESPERANDO_FAQ":
                    await handle_faq_query(phone_number, user_text, user_state, current_business_id, db)

                elif user_text.upper() in ["SI", "NO", "CANCELAR", "CONFIRMO", "CANCELO", "CAMBIO"]:
                    response_map = {
                        "SI": "confirmo", "CONFIRMO": "confirmo",
                        "NO": "cancelo", "CANCELAR": "cancelo", "CANCELO": "cancelo",
                        "CAMBIO": "cambio",
                    }
                    response_type = response_map.get(user_text.upper(), "desconocido")
                    log_event(
                        session_id=phone_number,
                        business_id=current_business_id,
                        event_type="reminder_response",
                        payload={"response_type": response_type, "raw_text": user_text},
                    )
                    await send_message(
                        phone=phone_number,
                        text="¡Gracias por tu respuesta! La hemos registrado.",
                    )
                    await handle_welcome_flow(phone_number, current_business_id, db)

                elif user_text.strip().isdigit() and 1 <= int(user_text.strip()) <= 5:
                    score = int(user_text.strip())
                    outcome = "turno_exitoso"
                    if user_state and user_state.get("estado") == "HUMAN_ESCALATION":
                        outcome = "escalado_exitoso"

                    log_event(
                        session_id=phone_number,
                        business_id=current_business_id,
                        event_type="csat_submitted",
                        payload={"score": score, "outcome": outcome},
                    )

                    try:
                        fb = Feedback(
                            business_id=current_business_id,
                            session_id=phone_number,
                            score=score,
                            outcome=outcome,
                            user_phone=phone_number,
                            submitted_at=datetime.now(timezone.utc),
                        )
                        db.add(fb)
                        db.commit()
                        logger.info(f"CSAT guardado en feedback: score={score}, outcome={outcome}")
                    except Exception:
                        db.rollback()
                        logger.exception("Error guardando CSAT en tabla feedback")

                    await send_message(
                        phone=phone_number,
                        text=f"¡Gracias por tu calificación de {score} estrellas! ⭐",
                    )
                    await handle_welcome_flow(phone_number, current_business_id, db)

                else:
                    await handle_text_fallback(phone_number, user_text, user_state, current_business_id, db)
                    
            # --- CASO B: RESPUESTAS INTERACTIVAS ---
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")
                
                if interactive_type == "button_reply":
                    reply = interactive_data.get("button_reply", {})
                    selected_id = reply.get("id")
                    button_title = reply.get("title", "")
                    logger.info(f"Botón presionado: ID={selected_id}, Título='{button_title}'")
                    
                    if current_step == "MENU_PRINCIPAL":
                        await handle_main_menu_selection(phone_number, selected_id, user_state, current_business_id, db)
                        
                    elif current_step == "MENU_TURNOS":
                        await handle_turnos_menu_selection(phone_number, selected_id, user_state, current_business_id, db)
                        
                    elif current_step == "CONFIRMA_PRODUCTO":
                        await handle_catalogo_menu_selection(phone_number, selected_id, user_state, current_business_id, db)
                        
                    elif current_step == "CONFIRMA_CANCELACION":
                        await handle_cancel_confirmation(phone_number, selected_id, user_state, current_business_id, db)

                    elif current_step == "ELIGE_FECHA" and selected_id.startswith("btn_fecha_"):
                        await handle_date_selection(phone_number, button_title, user_state, current_business_id, db)
                        
                    elif current_step == "ELIGE_HORARIO" and selected_id.startswith("btn_hora_"):
                        await handle_time_selection(phone_number, button_title, user_state, current_business_id, db)
                        
                    else:
                        await handle_welcome_flow(phone_number, current_business_id, db)
                        
                elif interactive_type == "list_reply":
                    reply = interactive_data.get("list_reply", {})
                    selected_id = reply.get("id")
                    row_title = reply.get("title", "")
                    logger.info(f"Opción de lista seleccionada por {phone_number}: ID={selected_id}, Título='{row_title}'")
                    
                    if current_step == "SELECCIONA_TURNO_CANCELAR" and selected_id.startswith("cancel_appt_"):
                        try:
                            appt_id = int(selected_id.replace("cancel_appt_", ""))
                            await handle_cancel_confirmation(phone_number, f"btn_confirm_cancel_{appt_id}", user_state, current_business_id, db)
                        except ValueError:
                            await send_message(phone_number, "Error al procesar la lista de cancelación.")
                            await clear_user_state(phone_number)
                    else:
                        await handle_list_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    
    except Exception as e:
        logger.error(f"Error procesando el webhook entrante: {str(e)}")
        
    return {"status": "success"}