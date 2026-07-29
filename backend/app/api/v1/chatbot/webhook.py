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
from app.db.models.faq import FAQ
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import get_user_state, set_user_state, clear_user_state
from app.services.event_logger import log_event
from app.services.negocio import get_active_services, get_available_slots, get_business_timezone, get_or_create_user
from app.services.catalog import get_products
from app.services.calendar import create_appointment, get_appointments_by_phone, cancel_appointment
from app.services.faq import search_faqs, get_faqs

logger = logging.getLogger(__name__)
router = APIRouter()

MOCK_BUSINESS_ID = 1

BOTONES_PRINCIPALES = [
    {"id": "btn_turnos", "title": "📅 Reservar Turno"},
    {"id": "btn_catalogo", "title": "🛍️ Catálogo"},
    {"id": "btn_faq", "title": "❓ Consultas"}
]

def get_business_name(db: Session, business_id: int) -> str:
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.name if business else "Nuestro Local"

def get_existing_user_name(db: Session, phone: str, business_id: int) -> str | None:
    user = db.query(User).filter(User.phone == phone, User.business_id == business_id).first()
    if user and user.name and user.name.strip() and not user.name.startswith("Cliente "):
        return user.name.strip()
    return None

async def _reset_demo_tenant(db: Session, phone_number: str, target_business_id: int, business_name: str):
    variants = {phone_number}
    if phone_number.startswith("541115"): variants.add("54911" + phone_number[6:])
    elif phone_number.startswith("54911"): variants.add("541115" + phone_number[5:])
    
    sessions = db.query(ChatSession).filter(or_(ChatSession.session_id.in_(variants), ChatSession.user_phone.in_(variants))).all()
    if sessions:
        for s in sessions: s.business_id = target_business_id
        db.commit()
    else:
        new_s = ChatSession(session_id=phone_number, business_id=target_business_id, user_phone=phone_number, status="active")
        db.add(new_s)
        db.commit()

    for v in variants: await clear_user_state(v)
    await send_message(phone=phone_number, text=f"✅ Demo cambiada a {business_name} (ID {target_business_id}).")

async def handle_welcome_flow(phone: str, business_id: int, db: Session):
    await clear_user_state(phone)
    await set_user_state(phone, {"estado": "MENU_PRINCIPAL", "step": 1})
    log_event(session_id=phone, business_id=business_id, event_type="conversation_started", payload={"is_new_user": True, "channel": "whatsapp"})
    
    nombre_negocio = get_business_name(db, business_id)
    known_name = get_existing_user_name(db, phone, business_id)
    greeting = f"¡Hola {known_name}! " if known_name else "¡Hola! "
    
    await send_interactive_buttons(phone=phone, body_text=f"{greeting}Bienvenido a *{nombre_negocio}*. ¿Qué deseas realizar?", buttons=BOTONES_PRINCIPALES)

async def handle_main_menu_selection(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    log_event(session_id=phone, business_id=business_id, event_type="menu_option_selected", payload={"option_name": button_id})
    nombre_negocio = get_business_name(db, business_id)

    if button_id == "btn_turnos":
        services = get_active_services(db, business_id)
        if not services:
            await send_message(phone=phone, text=f"💇‍♀️ {nombre_negocio} no tiene servicios disponibles en este momento.")
            return

        rows_services = [{"id": f"srv_{s.id}", "title": s.name[:24], "description": f"{s.duration_minutes or 30} min | ${float(s.price):,.0f}"[:72]} for s in services[:8]]
        sections = [
            {"title": "Selecciona un Servicio"[:20], "rows": rows_services},
            {"title": "Mi Cuenta"[:20], "rows": [
                {"id": "action_ver_turno", "title": "👀 Ver mi próximo turno", "description": "Consulta tu reserva activa"},
                {"id": "action_cancelar_turno", "title": "❌ Cancelar turno", "description": "Libera tu horario agendado"}
            ]}
        ]
        user_state["estado"] = "SELECCIONANDO_SERVICIO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        await send_interactive_list(phone=phone, body_text="Selecciona el servicio para tu cita o gestiona tus turnos:", button_label="Ver Opciones 📋", sections=sections, header_text="Agenda de Turnos", footer_text=nombre_negocio)

    elif button_id == "btn_catalogo":
        products = get_products(db, business_id)
        if not products:
            await send_message(phone=phone, text=f"🛒 {nombre_negocio} no tiene productos en catálogo actualmente.")
            return

        rows = [{"id": f"prod_{p.id}", "title": p.name[:24], "description": f"Stock: {p.stock_quantity or 0} | ${float(p.price):,.0f}"[:72]} for p in products[:10]]
        user_state["estado"] = "SELECCIONANDO_PRODUCTO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        await send_interactive_list(phone=phone, body_text="Selecciona el producto que deseas reservar para retiro en local:", button_label="Ver Productos 🛍️", sections=[{"title": "Catálogo"[:20], "rows": rows}], header_text="Catálogo de Productos", footer_text=nombre_negocio)

    elif button_id == "btn_faq":
        business = db.query(Business).filter(Business.id == business_id).first()
        rows = []
        
        # Inyección dinámica de la Configuración del Dashboard
        if business.horarios:
            rows.append({"id": "faq_sys_horarios", "title": "⏰ Horarios", "description": business.horarios[:72]})
        if business.contacto:
            rows.append({"id": "faq_sys_contacto", "title": "📞 Contacto", "description": business.contacto[:72]})
        
        pagos = []
        if business.accepts_cash: pagos.append("Efectivo")
        if business.accept_cards: pagos.append("Tarjetas")
        if pagos:
            rows.append({"id": "faq_sys_pagos", "title": "💳 Métodos de pago", "description": " y ".join(pagos)[:72]})
            
        faqs = get_faqs(db, business_id)
        for f in faqs:
            if len(rows) < 10:
                rows.append({"id": f"faq_{f.id}", "title": f.question[:24], "description": f.answer[:72]})
                
        if rows:
            user_state["estado"] = "SELECCIONANDO_FAQ"
            await set_user_state(phone, user_state)
            await send_interactive_list(phone=phone, body_text="Aquí tienes información útil sobre nuestro local:", button_label="Ver Info ❓", sections=[{"title": "Consultas Frecuentes"[:20], "rows": rows}])
        else:
            user_state["estado"] = "ESPERANDO_FAQ"
            await set_user_state(phone, user_state)
            await send_message(phone=phone, text="Escribe tu consulta y con gusto te responderemos:")

async def handle_service_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    if selected_id == "action_ver_turno":
        await handle_view_appointment(phone, user_state, business_id, db)
        return
    elif selected_id == "action_cancelar_turno":
        await handle_cancel_appointment_flow(phone, user_state, business_id, db)
        return

    svc_db_id = int(selected_id.replace("srv_", "")) if selected_id.startswith("srv_") else 1
    user_state["servicio_id"] = svc_db_id
    user_state["servicio_seleccionado"] = row_title

    today = date.today()
    tomorrow = today + timedelta(days=1)

    slots_today = get_available_slots(db, svc_db_id, business_id, today)
    slots_tomorrow = get_available_slots(db, svc_db_id, business_id, tomorrow)

    rows_today = [{"id": f"slot_{today.isoformat()}_{slot.strftime('%H%M')}", "title": f"Hoy {slot.strftime('%H:%M')} hs"[:24], "description": f"Turno para {row_title}"[:72]} for slot in slots_today[:4]]
    rows_tomorrow = [{"id": f"slot_{tomorrow.isoformat()}_{slot.strftime('%H%M')}", "title": f"Mañana {slot.strftime('%H:%M')} hs"[:24], "description": f"Turno para {row_title}"[:72]} for slot in slots_tomorrow[:5]]

    sections = []
    if rows_today: sections.append({"title": "Hoy"[:20], "rows": rows_today})
    if rows_tomorrow: sections.append({"title": "Mañana"[:20], "rows": rows_tomorrow})

    # PAGINACIÓN: Opción para ver más fechas
    sections.append({
        "title": "Más opciones"[:20],
        "rows": [{"id": f"action_mas_fechas_{svc_db_id}", "title": "📅 Elegir otra fecha", "description": "Ver disponibilidad próximos días"}]
    })

    user_state["estado"] = "SELECCIONANDO_SLOT"
    await set_user_state(phone, user_state)
    await send_interactive_list(phone=phone, body_text=f"Servicio: *{row_title}*.\nSelecciona el horario que mejor te convenga:", button_label="Ver Horarios ⏰", sections=sections)

async def handle_more_dates_selection(phone: str, selected_id: str, user_state: dict, business_id: int, db: Session):
    """Muestra los próximos 7 días disponibles."""
    svc_db_id = int(selected_id.replace("action_mas_fechas_", ""))
    user_state["servicio_id"] = svc_db_id
    await set_user_state(phone, user_state)
    
    today = date.today()
    rows = []
    for i in range(2, 9):
        target_date = today + timedelta(days=i)
        slots = get_available_slots(db, svc_db_id, business_id, target_date)
        if slots:
            rows.append({
                "id": f"date_{target_date.isoformat()}",
                "title": target_date.strftime("%d/%m/%Y"),
                "description": f"{len(slots)} horarios disponibles"
            })
    
    if not rows:
        await send_message(phone, "No hay fechas disponibles próximamente.")
        return
        
    await send_interactive_list(phone=phone, body_text="Selecciona la fecha que prefieras:", button_label="Ver Fechas 📅", sections=[{"title": "Próximos días"[:20], "rows": rows[:10]}])

async def handle_specific_date_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Muestra los horarios para una fecha específica elegida en la paginación."""
    fecha_iso = selected_id.replace("date_", "")
    target_date = date.fromisoformat(fecha_iso)
    svc_db_id = user_state.get("servicio_id", 1)
    
    slots = get_available_slots(db, svc_db_id, business_id, target_date)
    rows = [{"id": f"slot_{fecha_iso}_{slot.strftime('%H%M')}", "title": f"{slot.strftime('%H:%M')} hs"[:24], "description": "Horario disponible"} for slot in slots[:10]]
        
    await send_interactive_list(phone=phone, body_text=f"Horarios para el {row_title}:", button_label="Ver Horarios ⏰", sections=[{"title": "Horarios"[:20], "rows": rows}])

async def handle_slot_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    parts = selected_id.replace("slot_", "").split("_")
    user_state["fecha_iso"] = parts[0]
    user_state["hora_seleccionada"] = f"{parts[1][:2]}:{parts[1][2:]}"

    known_name = get_existing_user_name(db, phone, business_id)
    if known_name:
        await execute_appointment_creation(phone, known_name, user_state, business_id, db)
    else:
        user_state["estado"] = "ESPERANDO_NOMBRE_TURNO"
        await set_user_state(phone, user_state)
        await send_message(phone=phone, text=f"Elegiste *{row_title}*.\nPara confirmar, escribe tu *Nombre y Apellido* por teclado:")

async def execute_appointment_creation(phone: str, client_name: str, user_state: dict, business_id: int, db: Session):
    fecha_iso = user_state.get("fecha_iso", date.today().isoformat())
    hora_str = user_state.get("hora_seleccionada", "10:00")
    servicio_nombre = user_state.get("servicio_seleccionado", "Servicio General")
    servicio_id = user_state.get("servicio_id", 1)

    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)
    scheduled_date = datetime.strptime(f"{fecha_iso} {hora_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    user = get_or_create_user(db, phone, business_id, name=client_name.strip())

    appt_data = {
        "business_id": business_id, "user_id": user.id if user else None, "user_phone": phone,
        "user_name": client_name.strip()[:200], "service_id": servicio_id, "scheduled_date": scheduled_date,
        "status": "confirmed", "created_via": "chatbot", "session_id": phone
    }

    try:
        appointment = create_appointment(db, appt_data)
        log_event(session_id=phone, business_id=business_id, event_type="appointment_created", payload={"appointment_id": appointment.id, "via_bot": True, "servicio": servicio_nombre, "fecha": fecha_iso, "hora": hora_str})
        await send_message(phone=phone, text=f"🎉 *¡Turno Confirmado!*\n\n👤 *Cliente:* {client_name.strip()}\n💇‍♀️ *Servicio:* {servicio_nombre}\n📅 *Fecha:* {fecha_iso}\n⏰ *Hora:* {hora_str} hs\n\nTe esperamos en nuestro local. Si necesitas cancelar, escribe *Menú*.")
    except Exception as e:
        logger.error(f"Error creando turno: {e}")
        await send_message(phone, "Error al procesar la reserva. Intenta nuevamente.")
    
    await clear_user_state(phone)

async def handle_product_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    user_state["producto_seleccionado"] = row_title
    known_name = get_existing_user_name(db, phone, business_id)

    if known_name:
        await execute_product_reservation(phone, known_name, row_title, user_state, business_id, db)
    else:
        user_state["estado"] = "ESPERANDO_NOMBRE_CATALOGO"
        await set_user_state(phone, user_state)
        await send_message(phone=phone, text=f"Reservando: *{row_title}*.\nEscribe tu *Nombre y Apellido* para guardar tu pedido:")

async def execute_product_reservation(phone: str, client_name: str, product_name: str, user_state: dict, business_id: int, db: Session):
    user = get_or_create_user(db, phone, business_id, name=client_name.strip())
    await send_message(phone=phone, text=f"✅ ¡Pedido Guardado {client_name.strip()}!\n\nTu reserva de *{product_name}* está asentada. Puedes pasar a retirarlo por el local.")
    log_event(session_id=phone, business_id=business_id, event_type="conversation_closed", payload={"resultado_final": "producto_comprado", "producto": product_name})
    await clear_user_state(phone)

async def handle_view_appointment(phone: str, user_state: dict, business_id: int, db: Session):
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_message(phone=phone, text="👀 No tienes turnos próximos agendados.")
    else:
        next_appt = upcoming[0]
        service = db.query(Service).filter(Service.id == next_appt.service_id).first()
        tz_str = get_business_timezone(db, business_id)
        local_dt = next_appt.scheduled_date.astimezone(zoneinfo.ZoneInfo(tz_str))
        await send_message(phone=phone, text=f"👀 *Tu Próximo Turno:*\n\n👤 *Cliente:* {next_appt.user_name or 'Registrado'}\n💇‍♀️ *Servicio:* {service.name if service else 'Servicio'}\n📅 *Fecha:* {local_dt.strftime('%d/%m/%Y')}\n⏰ *Hora:* {local_dt.strftime('%H:%M')} hs")

    await clear_user_state(phone)

async def handle_cancel_appointment_flow(phone: str, user_state: dict, business_id: int, db: Session):
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_message(phone=phone, text="❌ No tienes turnos activos para cancelar.")
    else:
        appt = upcoming[0]
        if cancel_appointment(db=db, appointment_id=appt.id, business_id=business_id, reason="Cancelado por el cliente"):
            await send_message(phone=phone, text="✅ Tu turno ha sido cancelado con éxito. El horario fue liberado.")
        else:
            await send_message(phone=phone, text="⚠️ Ocurrió un inconveniente al cancelar tu turno.")
    await clear_user_state(phone)

async def handle_faq_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    """Responde las FAQs dinámicas del Dashboard o las de la Base de Datos."""
    biz = db.query(Business).filter(Business.id == business_id).first()
    
    if selected_id == "faq_sys_horarios":
        await send_message(phone, f"⏰ *Nuestros horarios son:*\n{biz.horarios or 'No especificado'}")
    elif selected_id == "faq_sys_contacto":
        await send_message(phone, f"📞 *Puedes contactarnos en:*\n{biz.contacto or 'No especificado'}")
    elif selected_id == "faq_sys_pagos":
        pagos = []
        if biz.accepts_cash: pagos.append("Efectivo")
        if biz.accept_cards: pagos.append("Tarjetas de crédito/débito")
        await send_message(phone, f"💳 *Métodos de pago aceptados:*\n{', '.join(pagos) if pagos else 'Consultar en el local'}")
    else:
        faq_id = int(selected_id.replace("faq_", ""))
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            await send_message(phone, f"💡 *{faq.question}*\n\n{faq.answer}")
            
    await clear_user_state(phone)

async def handle_faq_query(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    faqs_encontradas = search_faqs(db, business_id, user_text)
    if faqs_encontradas:
        faq = faqs_encontradas[0]
        await send_message(phone=phone, text=f"💡 *{faq.question}*\n\n{faq.answer}")
    else:
        await send_message(phone=phone, text="No encontré una respuesta exacta. Escribe *Menú* para volver a las opciones.")
    await clear_user_state(phone)

async def handle_text_fallback(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
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
async def verify_webhook(mode: str = Query(None, alias="hub.mode"), challenge: str = Query(None, alias="hub.challenge"), verify_token: str = Query(None, alias="hub.verify_token")):
    if mode == "subscribe" and verify_token and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)

def clean_phone_number(phone: str) -> str:
    return "541115" + phone[5:] if phone.startswith("54911") else phone

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
                    elif selected_id.startswith("action_mas_fechas_"):
                        await handle_more_dates_selection(phone_number, selected_id, user_state, current_business_id, db)
                    elif selected_id.startswith("date_"):
                        await handle_specific_date_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("slot_"):
                        await handle_slot_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("prod_"):
                        await handle_product_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("faq_"):
                        await handle_faq_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("cancel_appt_"):
                        try:
                            appt_id = int(selected_id.replace("cancel_appt_", ""))
                            await handle_cancel_appointment_flow(phone_number, user_state, current_business_id, db)
                        except ValueError:
                            await send_message(phone_number, "Error al procesar la lista de cancelación.")
                            await clear_user_state(phone_number)

    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")

    return {"status": "success"}