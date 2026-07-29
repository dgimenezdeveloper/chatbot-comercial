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
from app.db.models.user import User
from app.db.models.business import Business
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import get_user_state, set_user_state, clear_user_state
from app.services.event_logger import log_event
from app.services.negocio import get_active_services, get_available_slots, get_business_timezone, get_or_create_user
from app.services.catalog import get_products
from app.services.calendar import create_appointment, get_appointments_by_phone, cancel_appointment
from app.services.faq import search_faqs, get_faqs

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# CONSTANTES DE CONFIGURACIÓN Y MENÚS
# =============================================================================
MOCK_BUSINESS_ID = 1

BOTONES_PRINCIPALES = [
    {"id": "btn_turnos", "title": "📅 Reservar Turno"},
    {"id": "btn_catalogo", "title": "🛍️ Catálogo"},
    {"id": "btn_faq", "title": "❓ Consultas"}
]

# =============================================================================
# HELPERS
# =============================================================================

def get_business_name(db: Session, business_id: int) -> str:
    """Obtiene el nombre del negocio directamente desde la DB."""
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.name if business else "Nuestro Local"

def get_existing_user_name(db: Session, phone: str, business_id: int) -> str | None:
    """Retorna el nombre si el cliente ya está registrado y no es el fallback por defecto."""
    user = db.query(User).filter(User.phone == phone, User.business_id == business_id).first()
    if user and user.name and user.name.strip() and not user.name.startswith("Cliente "):
        return user.name.strip()
    return None

async def _reset_demo_tenant(db: Session, phone_number: str, target_business_id: int, business_name: str):
    """Reset para alternar tenants en caliente durante el Demo Day."""
    variants = {phone_number}
    if phone_number.startswith("541115"):
        variants.add("54911" + phone_number[6:])
    elif phone_number.startswith("54911"):
        variants.add("541115" + phone_number[5:])
    
    sessions = db.query(ChatSession).filter(
        or_(ChatSession.session_id.in_(variants), ChatSession.user_phone.in_(variants))
    ).all()
    
    if sessions:
        for s in sessions:
            s.business_id = target_business_id
        db.commit()
    else:
        new_s = ChatSession(session_id=phone_number, business_id=target_business_id, user_phone=phone_number, status="active")
        db.add(new_s)
        db.commit()

    for v in variants:
        await clear_user_state(v)

    await send_message(
        phone=phone_number,
        text=f"✅ Demo cambiada a {business_name} (ID {target_business_id})."
    )

# =============================================================================
# FLUJOS PRINCIPALES OPTIMIZADOS (REDUCCIÓN DE MENSAJES META)
# =============================================================================

async def handle_welcome_flow(phone: str, business_id: int, db: Session):
    """Bienvenida directa con botones principales."""
    await clear_user_state(phone)
    initial_state = {"estado": "MENU_PRINCIPAL", "step": 1}
    await set_user_state(phone, initial_state)

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="conversation_started",
        payload={"is_new_user": True, "channel": "whatsapp"},
    )
    
    nombre_negocio = get_business_name(db, business_id)
    known_name = get_existing_user_name(db, phone, business_id)
    greeting = f"¡Hola {known_name}! " if known_name else "¡Hola! "
    
    await send_interactive_buttons(
        phone=phone,
        body_text=f"{greeting}Bienvenido a *{nombre_negocio}*. ¿Qué deseas realizar?",
        buttons=BOTONES_PRINCIPALES
    )

async def handle_main_menu_selection(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    """Enruta las opciones del menú principal enviando directo la lista de servicios/productos."""
    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="menu_option_selected",
        payload={"option_name": button_id},
    )

    nombre_negocio = get_business_name(db, business_id)

    if button_id == "btn_turnos":
        services = get_active_services(db, business_id)
        if not services:
            await send_message(phone=phone, text=f"💇‍♀️ {nombre_negocio} no tiene servicios disponibles en este momento.")
            return

        rows_services = []
        for s in services[:8]:
            rows_services.append({
                "id": f"srv_{s.id}",
                "title": s.name[:24],
                "description": f"{s.duration_minutes or 30} min | ${float(s.price):,.0f}"[:72]
            })

        sections = [
            {"title": "Selecciona un Servicio"[:20], "rows": rows_services},
            {
                "title": "Mi Cuenta"[:20],
                "rows": [
                    {"id": "action_ver_turno", "title": "👀 Ver mi próximo turno", "description": "Consulta tu reserva activa"},
                    {"id": "action_cancelar_turno", "title": "❌ Cancelar turno", "description": "Libera tu horario agendado"}
                ]
            }
        ]

        user_state["estado"] = "SELECCIONANDO_SERVICIO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)

        await send_interactive_list(
            phone=phone,
            body_text="Selecciona el servicio para tu cita o gestiona tus turnos:",
            button_label="Ver Opciones 📋",
            sections=sections,
            header_text="Agenda de Turnos",
            footer_text=nombre_negocio
        )

    elif button_id == "btn_catalogo":
        products = get_products(db, business_id)
        if not products:
            await send_message(phone=phone, text=f"🛒 {nombre_negocio} no tiene productos en catálogo actualmente.")
            return

        rows = []
        for p in products[:10]:
            rows.append({
                "id": f"prod_{p.id}",
                "title": p.name[:24],
                "description": f"Stock: {p.stock_quantity or 0} | ${float(p.price):,.0f}"[:72]
            })

        user_state["estado"] = "SELECCIONANDO_PRODUCTO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)

        await send_interactive_list(
            phone=phone,
            body_text="Selecciona el producto que deseas reservar para retiro en local:",
            button_label="Ver Productos 🛍️",
            sections=[{"title": "Catálogo"[:20], "rows": rows}],
            header_text="Catálogo de Productos",
            footer_text=nombre_negocio
        )

    elif button_id == "btn_faq":
        faqs = get_faqs(db, business_id)
        if faqs:
            rows = [{"id": f"faq_{f.id}", "title": f.question[:24], "description": f.answer[:72]} for f in faqs[:10]]
            user_state["estado"] = "SELECCIONANDO_FAQ"
            await set_user_state(phone, user_state)
            await send_interactive_list(
                phone=phone,
                body_text="Preguntas frecuentes sobre nuestro local:",
                button_label="Ver Preguntas ❓",
                sections=[{"title": "Preguntas Frecuentes"[:20], "rows": rows}]
            )
        else:
            user_state["estado"] = "ESPERANDO_FAQ"
            await set_user_state(phone, user_state)
            await send_message(phone=phone, text="Escribe tu consulta y con gusto te responderemos:")

# =============================================================================
# SELECCIÓN UNIFICADA (SLOTS DE FECHA Y HORA EN 1 SOLO MENÚ)
# =============================================================================

async def handle_service_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Al elegir un servicio, calcula y envía directamente los slots combinados (Día + Hora) en 1 solo mensaje."""
    if selected_id == "action_ver_turno":
        await handle_view_appointment(phone, user_state, business_id, db)
        return
    elif selected_id == "action_cancelar_turno":
        await handle_cancel_appointment_flow(phone, user_state, business_id, db)
        return

    try:
        svc_db_id = int(selected_id.replace("srv_", ""))
    except ValueError:
        svc_db_id = 1

    user_state["servicio_id"] = svc_db_id
    user_state["servicio_seleccionado"] = row_title

    # Calcular slots libres para Hoy y Mañana
    today = date.today()
    tomorrow = today + timedelta(days=1)

    slots_today = get_available_slots(db, svc_db_id, business_id, today)
    slots_tomorrow = get_available_slots(db, svc_db_id, business_id, tomorrow)

    rows_today = []
    for slot in slots_today[:4]:
        time_str = slot.strftime("%H:%M")
        rows_today.append({
            "id": f"slot_{today.isoformat()}_{slot.strftime('%H%M')}",
            "title": f"Hoy {time_str} hs"[:24],
            "description": f"Turno para {row_title}"[:72]
        })

    rows_tomorrow = []
    for slot in slots_tomorrow[:4]:
        time_str = slot.strftime("%H:%M")
        rows_tomorrow.append({
            "id": f"slot_{tomorrow.isoformat()}_{slot.strftime('%H%M')}",
            "title": f"Mañana {time_str} hs"[:24],
            "description": f"Turno para {row_title}"[:72]
        })

    sections = []
    if rows_today:
        sections.append({"title": "Hoy"[:20], "rows": rows_today})
    if rows_tomorrow:
        sections.append({"title": "Mañana"[:20], "rows": rows_tomorrow})

    if not sections:
        await send_message(phone=phone, text=f"No hay horarios disponibles para *{row_title}* hoy o mañana. Por favor intenta más tarde.")
        await handle_welcome_flow(phone, business_id, db)
        return

    user_state["estado"] = "SELECCIONANDO_SLOT"
    await set_user_state(phone, user_state)

    await send_interactive_list(
        phone=phone,
        body_text=f"Servicio: *{row_title}*.\nSelecciona el horario que mejor te convenga:",
        button_label="Ver Horarios ⏰",
        sections=sections
    )

async def handle_slot_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Procesa el horario elegido y confirma inmediatamente si el cliente ya es conocido."""
    parts = selected_id.replace("slot_", "").split("_")
    fecha_iso = parts[0]
    hora_raw = parts[1]
    hora_str = f"{hora_raw[:2]}:{hora_raw[2:]}"

    user_state["fecha_iso"] = fecha_iso
    user_state["hora_seleccionada"] = hora_str

    known_name = get_existing_user_name(db, phone, business_id)

    if known_name:
        # CLIENTE CONOCIDO -> CONFIRMACIÓN INSTANTÁNEA (AHORRA 1 MENSAJE Y NUNCA SE CUELGA)
        await execute_appointment_creation(phone, known_name, user_state, business_id, db)
    else:
        # CLIENTE NUEVO -> PEDIR NOMBRE
        user_state["estado"] = "ESPERANDO_NOMBRE_TURNO"
        await set_user_state(phone, user_state)
        await send_message(phone=phone, text=f"Elegiste *{row_title}*.\nPara confirmar, escribe tu *Nombre y Apellido* por teclado:")

async def execute_appointment_creation(phone: str, client_name: str, user_state: dict, business_id: int, db: Session):
    """Persiste la cita en DB y notifica."""
    fecha_iso = user_state.get("fecha_iso", date.today().isoformat())
    hora_str = user_state.get("hora_seleccionada", "10:00")
    servicio_nombre = user_state.get("servicio_seleccionado", "Servicio General")
    servicio_id = user_state.get("servicio_id", 1)

    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)
    dt_str = f"{fecha_iso} {hora_str}"
    scheduled_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    user = get_or_create_user(db, phone, business_id, name=client_name.strip())

    appt_data = {
        "business_id": business_id,
        "user_id": user.id if user else None,
        "user_phone": phone,
        "user_name": client_name.strip()[:200],
        "service_id": servicio_id,
        "scheduled_date": scheduled_date,
        "status": "confirmed",
        "created_via": "chatbot",
        "session_id": phone
    }

    try:
        appointment = create_appointment(db, appt_data)
        appt_id = appointment.id
    except Exception as e:
        logger.error(f"Error creando turno: {e}")
        await send_message(phone, "Error al procesar la reserva. Intenta nuevamente.")
        await clear_user_state(phone)
        return

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="appointment_created",
        payload={"appointment_id": appt_id, "via_bot": True, "servicio": servicio_nombre, "fecha": fecha_iso, "hora": hora_str},
    )

    confirm_msg = (
        f"🎉 *¡Turno Confirmado!*\n\n"
        f"👤 *Cliente:* {client_name.strip()}\n"
        f"💇‍♀️ *Servicio:* {servicio_nombre}\n"
        f"📅 *Fecha:* {fecha_iso}\n"
        f"⏰ *Hora:* {hora_str} hs\n\n"
        f"Te esperamos en nuestro local. Si necesitas cancelar, escribe *Menú*."
    )
    await send_message(phone=phone, text=confirm_msg)
    await clear_user_state(phone)

# =============================================================================
# PRODUCTOS Y CATÁLOGO OPTIMIZADOS
# =============================================================================

async def handle_product_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Procesa el producto seleccionado del catálogo."""
    user_state["producto_seleccionado"] = row_title
    known_name = get_existing_user_name(db, phone, business_id)

    if known_name:
        await execute_product_reservation(phone, known_name, row_title, user_state, business_id, db)
    else:
        user_state["estado"] = "ESPERANDO_NOMBRE_CATALOGO"
        await set_user_state(phone, user_state)
        await send_message(phone=phone, text=f"Reservando: *{row_title}*.\nEscribe tu *Nombre y Apellido* para guardar tu pedido:")

async def execute_product_reservation(phone: str, client_name: str, product_name: str, user_state: dict, business_id: int, db: Session):
    """Finaliza la reserva de producto guardando el perfil."""
    user = get_or_create_user(db, phone, business_id, name=client_name.strip())

    await send_message(
        phone=phone,
        text=f"✅ ¡Pedido Guardado {client_name.strip()}!\n\nTu reserva de *{product_name}* está asentada. Puedes pasar a retirarlo por el local."
    )

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="conversation_closed",
        payload={"resultado_final": "producto_comprado", "producto": product_name},
    )
    await clear_user_state(phone)

# =============================================================================
# CONSULTA Y CANCELACIÓN
# =============================================================================

async def handle_view_appointment(phone: str, user_state: dict, business_id: int, db: Session):
    """Consulta rápida de turnos futuros."""
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_message(phone=phone, text="👀 No tienes turnos próximos agendados.")
    else:
        next_appt = upcoming[0]
        service = db.query(Service).filter(Service.id == next_appt.service_id).first()
        svc_name = service.name if service else "Servicio"
        tz_str = get_business_timezone(db, business_id)
        local_dt = next_appt.scheduled_date.astimezone(zoneinfo.ZoneInfo(tz_str))

        msg = (
            f"👀 *Tu Próximo Turno:*\n\n"
            f"👤 *Cliente:* {next_appt.user_name or 'Registrado'}\n"
            f"💇‍♀️ *Servicio:* {svc_name}\n"
            f"📅 *Fecha:* {local_dt.strftime('%d/%m/%Y')}\n"
            f"⏰ *Hora:* {local_dt.strftime('%H:%M')} hs"
        )
        await send_message(phone=phone, text=msg)

    await clear_user_state(phone)

async def handle_cancel_appointment_flow(phone: str, user_state: dict, business_id: int, db: Session):
    """Cancelación de turno."""
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_message(phone=phone, text="❌ No tienes turnos activos para cancelar.")
        await clear_user_state(phone)
        return

    appt = upcoming[0]
    canceled_appt = cancel_appointment(db=db, appointment_id=appt.id, business_id=business_id, reason="Cancelado por el cliente")

    if canceled_appt:
        await send_message(phone=phone, text="✅ Tu turno ha sido cancelado con éxito. El horario fue liberado.")
    else:
        await send_message(phone=phone, text="⚠️ Ocurrió un inconveniente al cancelar tu turno.")

    await clear_user_state(phone)

async def handle_faq_query(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    """Busca respuestas FAQ."""
    faqs_encontradas = search_faqs(db, business_id, user_text)
    if faqs_encontradas:
        faq = faqs_encontradas[0]
        await send_message(phone=phone, text=f"💡 *{faq.question}*\n\n{faq.answer}")
    else:
        await send_message(phone=phone, text="No encontré una respuesta exacta. Escribe *Menú* para volver a las opciones.")
    await clear_user_state(phone)

async def handle_text_fallback(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    """Fallback si no entiende la entrada."""
    fallback_n = user_state.get("fallback_count", 0) + 1
    user_state["fallback_count"] = fallback_n

    if fallback_n >= 2:
        user_state["estado"] = "HUMAN_ESCALATION"
        await set_user_state(phone, user_state)
        await send_message(phone=phone, text="Un representante humano revisará tu mensaje a la brevedad.")
        return

    await send_message(phone=phone, text="Por favor selecciona una opción del menú o escribe *Menú* para reiniciar.")

# =============================================================================
# ENRUTADOR PRINCIPAL (WEBHOOK ENDPOINT)
# =============================================================================

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    challenge: str = Query(None, alias="hub.challenge"),
    verify_token: str = Query(None, alias="hub.verify_token")
):
    if mode == "subscribe" and verify_token and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)

def clean_phone_number(phone: str) -> str:
    if phone.startswith("54911"):
        return "541115" + phone[5:]
    return phone

@router.post("/webhook")
async def receive_webhook(payload: dict, db: Session = Depends(get_db)):
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message = messages[0]
            phone_number = message.get("from")
            message_type = message.get("type")

            if settings.APP_ENV == "development" and phone_number.startswith("549"):
                phone_number = f"54{phone_number[3:5]}15{phone_number[5:]}"
            else:
                phone_number = clean_phone_number(phone_number)

            db_session = db.query(ChatSession).filter(ChatSession.session_id == phone_number).first()
            if not db_session:
                db_session = ChatSession(session_id=phone_number, business_id=MOCK_BUSINESS_ID, user_phone=phone_number, status="active")
                db.add(db_session)
                db.commit()

            current_business_id = db_session.business_id
            user_state = await get_user_state(phone_number)
            current_step = user_state.get("estado") if user_state else "NUEVO"

            # 1. TEXTO PLANO
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()

                if user_text.lower() == "/reset_demo estetica":
                    await _reset_demo_tenant(db, phone_number, 1, "Peluquería")
                    return {"status": "success"}
                elif user_text.lower() == "/reset_demo barberia":
                    await _reset_demo_tenant(db, phone_number, 2, "Barbería")
                    return {"status": "success"}

                if user_text.lower() in ["hola", "menu", "menú", "volver", "comenzar"] or current_step == "NUEVO":
                    await handle_welcome_flow(phone_number, current_business_id, db)
                elif current_step == "ESPERANDO_NOMBRE_TURNO":
                    await execute_appointment_creation(phone_number, user_text, user_state, current_business_id, db)
                elif current_step == "ESPERANDO_NOMBRE_CATALOGO":
                    prod_name = user_state.get("producto_seleccionado", "Producto")
                    await execute_product_reservation(phone_number, user_text, prod_name, user_state, current_business_id, db)
                elif current_step in ["ESPERANDO_FAQ", "SELECCIONANDO_FAQ"]:
                    await handle_faq_query(phone_number, user_text, user_state, current_business_id, db)
                else:
                    await handle_text_fallback(phone_number, user_text, user_state, current_business_id, db)

            # 2. RESPUESTAS INTERACTIVAS (BOTONES Y LISTAS)
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")

                if interactive_type == "button_reply":
                    selected_id = interactive_data.get("button_reply", {}).get("id")
                    if current_step == "MENU_PRINCIPAL":
                        await handle_main_menu_selection(phone_number, selected_id, user_state, current_business_id, db)
                    else:
                        await handle_welcome_flow(phone_number, current_business_id, db)

                elif interactive_type == "list_reply":
                    list_data = interactive_data.get("list_reply", {})
                    selected_id = list_data.get("id")
                    row_title = list_data.get("title", "")

                    if selected_id.startswith("srv_") or selected_id.startswith("action_"):
                        await handle_service_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("slot_"):
                        await handle_slot_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("prod_"):
                        await handle_product_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("faq_"):
                        await handle_faq_query(phone_number, row_title, user_state, current_business_id, db)

    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")

    return {"status": "success"}