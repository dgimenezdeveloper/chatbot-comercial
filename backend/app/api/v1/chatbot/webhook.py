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
from app.db.models.product import Product
from app.db.models.user import User
from app.db.models.business import Business
from app.db.models.faq import FAQ
from app.db.models.appointment import Appointment
from app.services.whatsapp import send_message, send_interactive_buttons, send_interactive_list
from app.services.state_manager import (
    get_user_state, set_user_state, clear_user_state,
    create_human_proxy, get_client_by_short_id, close_human_proxy
)
from app.services.event_logger import log_event
from app.services.negocio import get_active_services, get_available_slots, get_business_timezone, get_or_create_user
from app.services.catalog import get_products
from app.services.calendar import create_appointment, get_appointments_by_phone, cancel_appointment
from app.services.faq import search_faqs, get_faqs

logger = logging.getLogger(__name__)
router = APIRouter()

MOCK_BUSINESS_ID = 1

BOTONES_PRINCIPALES = [
    {"id": "btn_turnos", "title": "📅 Gestión de Turnos"},
    {"id": "btn_catalogo", "title": "🛍️ Catálogo"},
    {"id": "btn_faq", "title": "❓ Consultas"}
]

# =============================================================================
# HELPERS DE TELÉFONO, NEGOCIO Y VALIDACIÓN DE ESTADO
# =============================================================================

def get_business_name(db: Session, business_id: int) -> str:
    business = db.query(Business).filter(Business.id == business_id).first()
    return business.name if business else "Nuestro Local"

def get_existing_user_name(db: Session, phone: str, business_id: int) -> str | None:
    user = db.query(User).filter(User.phone == phone, User.business_id == business_id).first()
    if user and user.name and user.name.strip() and not user.name.startswith("Cliente "):
        return user.name.strip()
    return None

def format_phone_for_meta(phone: str | None) -> str | None:
    """Extrae solo dígitos para enviar a Meta Cloud API (E.164 puro)."""
    if not phone: return None
    return "".join(c for c in phone if c.isdigit())

def clean_phone_number(phone: str | None) -> str:
    """Limpia el número dejando solo dígitos."""
    if not phone: return ""
    return "".join(c for c in phone if c.isdigit())

def is_same_phone(phone1: str | None, phone2: str | None) -> bool:
    """Compara dos teléfonos por sus últimos 8 dígitos."""
    if not phone1 or not phone2: return False
    p1 = format_phone_for_meta(phone1)
    p2 = format_phone_for_meta(phone2)
    if not p1 or not p2: return False
    return p1[-8:] == p2[-8:] if len(p1) >= 8 and len(p2) >= 8 else p1 == p2

def is_action_valid_for_state(selected_id: str, current_step: str) -> bool:
    """Valida si la opción interactiva elegida pertenece al paso conversacional activo."""
    if selected_id in ["btn_volver_menu", "btn_turnos", "btn_catalogo", "btn_faq"] or selected_id.startswith("rem_") or selected_id.startswith("btn_mod_appt_") or selected_id.startswith("btn_confirm_cancel_"):
        return True

    if current_step == "NUEVO":
        return True

    allowed_prefixes_per_state = {
        "MENU_PRINCIPAL": ["srv_", "action_ver_turno", "action_cancelar_turno", "prod_", "faq_", "btn_hablar_humano"],
        "SELECCIONANDO_SERVICIO": ["srv_", "action_ver_turno", "action_cancelar_turno"],
        "CONFIRMANDO_MAS_SERVICIOS": ["btn_agregar_servicio", "btn_continuar_fecha"],
        "SELECCIONANDO_FECHA": ["date_"],
        "SELECCIONANDO_SLOT": ["slot_", "page_slot_", "btn_continuar_fecha"],
        "SELECCIONANDO_PRODUCTO": ["prod_"],
        "CONFIRMANDO_MAS_PRODUCTOS": ["btn_agregar_producto", "btn_finalizar_pedido"],
        "SELECCIONANDO_FAQ": ["faq_", "btn_hablar_humano"],
        "ESPERANDO_FAQ": ["faq_", "btn_hablar_humano"],
        "CONFIRMA_CANCELACION": ["btn_confirm_cancel_"],
        "SELECCIONA_TURNO_CANCELAR": ["cancel_appt_", "btn_confirm_cancel_"],
    }

    allowed = allowed_prefixes_per_state.get(current_step, [])
    return any(selected_id.startswith(prefix) or selected_id == prefix for prefix in allowed)

async def _reset_demo_tenant(db: Session, phone_number: str, target_business_id: int, business_name: str):
    variants = {phone_number}
    sessions = db.query(ChatSession).filter(or_(ChatSession.session_id.in_(variants), ChatSession.user_phone.in_(variants))).all()
    if sessions:
        for s in sessions: s.business_id = target_business_id
        db.commit()
    else:
        new_s = ChatSession(session_id=phone_number, business_id=target_business_id, user_phone=phone_number, status="active")
        db.add(new_s)
        db.commit()

    await clear_user_state(phone_number)
    await send_message(phone=phone_number, text=f"✅ Demo cambiada a {business_name} (ID {target_business_id}).")

# =============================================================================
# DERIVACIÓN A HUMANO (HANDOVER PROTOCOL)
# =============================================================================

async def trigger_human_escalation(phone: str, user_text: str, user_state: dict, business_id: int, db: Session, reason: str = "user_request"):
    biz = db.query(Business).filter(Business.id == business_id).first()
    raw_owner_phone = biz.owner_phone if (biz and biz.owner_phone) else "5491162193426"
    owner_phone = format_phone_for_meta(raw_owner_phone)

    log_event(
        session_id=phone,
        business_id=business_id,
        event_type="escalation_to_human",
        payload={"reason": reason, "initial_text": user_text, "owner_phone": raw_owner_phone},
    )

    if not owner_phone or is_same_phone(raw_owner_phone, phone):
        logger.warning(f"[HANDOVER] Owner phone no configurado o idéntico al cliente ({phone}). Retornando al menú.")
        await send_interactive_buttons(
            phone=phone,
            body_text="En este momento nuestros representantes no están disponibles. ¿En qué más podemos ayudarte?",
            buttons=BOTONES_PRINCIPALES
        )
        await clear_user_state(phone)
        return

    short_id = await create_human_proxy(business_id, phone)
    known_name = get_existing_user_name(db, phone, business_id) or f"Cliente ({phone[-4:]})"

    owner_msg = (
        f"🚨 *Atención Requerida [#{short_id}]*\n\n"
        f"👤 *Cliente:* {known_name}\n"
        f"📞 *Teléfono:* {phone}\n"
        f"💬 *Mensaje:* \"{user_text}\"\n\n"
        f"👉 *Para responder:* Escribe `{short_id} tu respuesta`\n"
        f"🔒 *Para cerrar chat:* Escribe `{short_id} #fin`"
    )

    sent_to_owner = await send_message(owner_phone, owner_msg)

    if not sent_to_owner:
        logger.warning(f"[QA BYPASS] Falló la notificación al dueño ({owner_phone}), pero forzaremos la derivación para testing.")

    user_state["estado"] = "HUMAN_ESCALATION"
    await set_user_state(phone, user_state)

    await send_interactive_buttons(
        phone=phone,
        body_text="Te estamos transfiriendo con un representante humano. Te responderemos por este medio a la brevedad.",
        buttons=[{"id": "btn_volver_menu", "title": "🔙 Cancelar y Volver"}]
    )

# =============================================================================
# FLUJOS PRINCIPALES
# =============================================================================

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
        if user_state.get("estado") != "CONFIRMANDO_MAS_SERVICIOS":
            user_state["servicios"] = []
            
        services = get_active_services(db, business_id)
        if not services:
            await send_message(phone=phone, text=f"💇‍♀️ {nombre_negocio} no tiene servicios disponibles en este momento.")
            return

        rows_services = [{"id": f"srv_{s.id}", "title": s.name[:24], "description": f"{s.duration_minutes or 30} min | ${float(s.price):,.0f}"[:72]} for s in services[:7]]
        sections = [
            {"title": "Selecciona un Servicio"[:24], "rows": rows_services},
            {"title": "Mi Cuenta"[:24], "rows": [
                {"id": "action_ver_turno", "title": "👀 Ver mi próximo turno", "description": "Consulta tu reserva activa"},
                {"id": "action_cancelar_turno", "title": "❌ Cancelar turno", "description": "Libera tu horario agendado"}
            ]},
            {"title": "Navegación"[:24], "rows": [
                {"id": "btn_volver_menu", "title": "🔙 Menú Principal", "description": "Volver al inicio"}
            ]}
        ]
        user_state["estado"] = "SELECCIONANDO_SERVICIO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        await send_interactive_list(phone=phone, body_text="Selecciona el servicio para tu cita o gestiona tus turnos:", button_label="Ver Opciones 📋", sections=sections, header_text="Agenda de Turnos", footer_text=nombre_negocio)

    elif button_id == "btn_catalogo":
        if user_state.get("estado") != "CONFIRMANDO_MAS_PRODUCTOS":
            user_state["productos"] = []
            
        products = get_products(db, business_id)
        if not products:
            await send_message(phone=phone, text=f"🛒 {nombre_negocio} no tiene productos en catálogo actualmente.")
            return

        rows = [{"id": f"prod_{p.id}", "title": p.name[:24], "description": f"Stock: {p.stock_quantity or 0} | ${float(p.price):,.0f}"[:72]} for p in products[:9]]
        sections = [
            {"title": "Catálogo"[:24], "rows": rows},
            {"title": "Navegación"[:24], "rows": [
                {"id": "btn_volver_menu", "title": "🔙 Menú Principal", "description": "Volver al inicio"}
            ]}
        ]
        user_state["estado"] = "SELECCIONANDO_PRODUCTO"
        user_state["step"] += 1
        await set_user_state(phone, user_state)
        await send_interactive_list(phone=phone, body_text="Selecciona el producto que deseas reservar para retiro en local:", button_label="Ver Productos 🛍️", sections=sections, header_text="Catálogo de Productos", footer_text=nombre_negocio)

    elif button_id == "btn_faq":
        business = db.query(Business).filter(Business.id == business_id).first()
        rows = []
        
        if business.horarios: rows.append({"id": "faq_sys_horarios", "title": "⏰ Horarios", "description": business.horarios[:72]})
        if business.contacto: rows.append({"id": "faq_sys_contacto", "title": "📞 Contacto", "description": business.contacto[:72]})
        
        pagos = []
        if business.accepts_cash: pagos.append("Efectivo")
        if business.accept_cards: pagos.append("Tarjetas")
        if pagos: rows.append({"id": "faq_sys_pagos", "title": "💳 Métodos de pago", "description": " y ".join(pagos)[:72]})
            
        faqs = get_faqs(db, business_id)
        for f in faqs:
            if len(rows) < 8:
                rows.append({"id": f"faq_{f.id}", "title": f.question[:24], "description": f.answer[:72]})
        
        rows.append({"id": "btn_hablar_humano", "title": "👤 Hablar con un humano", "description": "Conectar con un representante real"})

        sections = [
            {"title": "Consultas Frecuentes"[:24], "rows": rows},
            {"title": "Navegación"[:24], "rows": [
                {"id": "btn_volver_menu", "title": "🔙 Menú Principal", "description": "Volver al inicio"}
            ]}
        ]

        user_state["estado"] = "SELECCIONANDO_FAQ"
        await set_user_state(phone, user_state)
        await send_interactive_list(phone=phone, body_text="Aquí tienes información útil sobre nuestro local:", button_label="Ver Info ❓", sections=sections)

# =============================================================================
# SELECCIÓN UNIFICADA (SLOTS DE FECHA Y HORA)
# =============================================================================

async def handle_service_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    if selected_id == "action_ver_turno":
        await handle_view_appointment(phone, user_state, business_id, db)
        return
    elif selected_id == "action_cancelar_turno":
        await handle_cancel_appointment_flow(phone, user_state, business_id, db)
        return

    svc_db_id = int(selected_id.replace("srv_", "")) if selected_id.startswith("srv_") else 1
    service = db.query(Service).filter(Service.id == svc_db_id).first()
    if not service:
        await send_message(phone, "Servicio no encontrado.")
        return

    servicios = user_state.get("servicios", [])
    servicios.append({
        "id": svc_db_id,
        "name": service.name,
        "duration": service.duration_minutes or 30,
        "price": float(service.price or 0)
    })
    user_state["servicios"] = servicios
    user_state["estado"] = "CONFIRMANDO_MAS_SERVICIOS"
    await set_user_state(phone, user_state)

    total_price = sum(s["price"] for s in servicios)
    total_duration = sum(s["duration"] for s in servicios)
    names = ", ".join(s["name"] for s in servicios)

    body_text = f"Has seleccionado: *{names}*.\nDuración total aprox: {total_duration} min.\nTotal: ${total_price:,.0f}.\n\n¿Deseas agregar otro servicio?"
    buttons = [
        {"id": "btn_agregar_servicio", "title": "➕ Agregar otro"},
        {"id": "btn_continuar_fecha", "title": "✅ Continuar"}
    ]
    await send_interactive_buttons(phone=phone, body_text=body_text, buttons=buttons)

async def show_date_selection(phone: str, user_state: dict, business_id: int, db: Session):
    today = date.today()
    rows = []
    
    servicios = user_state.get("servicios", [])
    if not servicios:
        await handle_main_menu_selection(phone, "btn_turnos", user_state, business_id, db)
        return
        
    total_duration = sum(s["duration"] for s in servicios)
    
    days_checked = 0
    current_date = today
    
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    while len(rows) < 9 and days_checked < 30:
        slots = get_available_slots(db, total_duration, business_id, current_date)
        if slots:
            if current_date == today:
                title = f"Hoy {current_date.day} de {meses[current_date.month - 1]}"
            elif current_date == today + timedelta(days=1):
                title = f"Mañana {current_date.day} de {meses[current_date.month - 1]}"
            else:
                title = f"{dias[current_date.weekday()]} {current_date.day} de {meses[current_date.month - 1]}"
                
            rows.append({
                "id": f"date_{current_date.isoformat()}",
                "title": title[:24],
                "description": f"{len(slots)} horarios disponibles"[:72]
            })
        current_date += timedelta(days=1)
        days_checked += 1

    if not rows:
        await send_interactive_buttons(phone=phone, body_text="No hay fechas disponibles próximamente.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
        return

    sections = [
        {"title": "Fechas Disponibles"[:24], "rows": rows},
        {"title": "Navegación"[:24], "rows": [{"id": "btn_volver_menu", "title": "🔙 Menú Principal", "description": "Volver al inicio"}]}
    ]
    
    user_state["estado"] = "SELECCIONANDO_FECHA"
    await set_user_state(phone, user_state)
    await send_interactive_list(phone=phone, body_text="Selecciona la fecha para tu turno:", button_label="Ver Fechas 📅", sections=sections)

async def handle_date_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    if selected_id.startswith("date_"):
        fecha_iso = selected_id.replace("date_", "")
        user_state["fecha_iso"] = fecha_iso
        page = 0
    elif selected_id.startswith("page_slot_"):
        page = int(selected_id.replace("page_slot_", ""))
        fecha_iso = user_state.get("fecha_iso")
    else:
        fecha_iso = user_state.get("fecha_iso")
        page = 0
        
    if not fecha_iso:
        await show_date_selection(phone, user_state, business_id, db)
        return
        
    target_date = date.fromisoformat(fecha_iso)
    servicios = user_state.get("servicios", [])
    total_duration = sum(s["duration"] for s in servicios)
    
    slots = get_available_slots(db, total_duration, business_id, target_date)
    
    items_per_page = 8
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_slots = slots[start_idx:end_idx]
    
    rows = [{"id": f"slot_{fecha_iso}_{slot.strftime('%H%M')}", "title": f"{slot.strftime('%H:%M')} hs"[:24], "description": "Horario disponible"} for slot in current_slots]
    
    nav_rows = []
    if end_idx < len(slots):
        nav_rows.append({"id": f"page_slot_{page + 1}", "title": "➡️ Más horarios", "description": "Ver más horarios para este día"})
    nav_rows.append({"id": "btn_continuar_fecha", "title": "📅 Elegir otra fecha", "description": "Volver a la selección de fecha"})
    nav_rows.append({"id": "btn_volver_menu", "title": "🔙 Menú Principal", "description": "Volver al inicio"})

    sections = [
        {"title": "Horarios"[:24], "rows": rows},
        {"title": "Navegación"[:24], "rows": nav_rows}
    ]
    
    user_state["estado"] = "SELECCIONANDO_SLOT"
    await set_user_state(phone, user_state)
    
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    date_str = f"{dias[target_date.weekday()]} {target_date.day} de {meses[target_date.month - 1]}"
    
    await send_interactive_list(phone=phone, body_text=f"Horarios para el *{date_str}*:", button_label="Ver Horarios ⏰", sections=sections)

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
        servicios = user_state.get("servicios", [])
        names = ", ".join(s["name"] for s in servicios)
        await send_message(phone=phone, text=f"Elegiste *{names}* el {parts[0]} a las {user_state['hora_seleccionada']} hs.\nPara confirmar, escribe tu *Nombre y Apellido* por teclado:")

async def execute_appointment_creation(phone: str, client_name: str, user_state: dict, business_id: int, db: Session):
    fecha_iso = user_state.get("fecha_iso", date.today().isoformat())
    hora_str = user_state.get("hora_seleccionada", "10:00")
    servicios = user_state.get("servicios", [])
    
    if not servicios:
        await send_message(phone, "Error: No hay servicios seleccionados.")
        return

    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)
    start_time = datetime.strptime(f"{fecha_iso} {hora_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

    user = get_or_create_user(db, phone, business_id, name=client_name.strip())

    current_time = start_time
    created_appts = []
    for s in servicios:
        appt_data = {
            "business_id": business_id, "user_id": user.id if user else None, "user_phone": phone,
            "user_name": client_name.strip()[:200], "service_id": s["id"], "scheduled_date": current_time,
            "status": "confirmed", "created_via": "chatbot", "session_id": phone
        }
        try:
            appointment = create_appointment(db, appt_data)
            created_appts.append(appointment)
            current_time += timedelta(minutes=s["duration"])
        except Exception as e:
            logger.error(f"Error creando turno para servicio {s['id']}: {e}")

    names = ", ".join(s["name"] for s in servicios)
    if created_appts:
        log_event(session_id=phone, business_id=business_id, event_type="appointment_created", payload={"appointment_ids": [a.id for a in created_appts], "via_bot": True, "servicios": names, "fecha": fecha_iso, "hora": hora_str})
        confirm_msg = f"🎉 *¡Turno Confirmado!*\n\n👤 *Cliente:* {client_name.strip()}\n💇‍♀️ *Servicios:* {names}\n📅 *Fecha:* {fecha_iso}\n⏰ *Hora de inicio:* {hora_str} hs\n\nTe esperamos en nuestro local."
        await send_interactive_buttons(phone=phone, body_text=confirm_msg, buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
    else:
        await send_interactive_buttons(phone=phone, body_text="Error al procesar la reserva. Intenta nuevamente.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
    
    await clear_user_state(phone)

# =============================================================================
# PRODUCTOS Y CATÁLOGO
# =============================================================================

async def handle_product_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    prod_db_id = int(selected_id.replace("prod_", ""))
    product = db.query(Product).filter(Product.id == prod_db_id).first()
    if not product:
        await send_message(phone, "Producto no encontrado.")
        return

    productos = user_state.get("productos", [])
    productos.append({
        "id": prod_db_id,
        "name": product.name,
        "price": float(product.price or 0)
    })
    user_state["productos"] = productos
    user_state["estado"] = "CONFIRMANDO_MAS_PRODUCTOS"
    await set_user_state(phone, user_state)

    total_price = sum(p["price"] for p in productos)
    names = "\n- ".join(p["name"] for p in productos)

    body_text = f"Has agregado: *{product.name}*.\n\nCarrito actual:\n{names}\nTotal: ${total_price:,.0f}.\n\n¿Deseas agregar otro producto?"
    buttons = [
        {"id": "btn_agregar_producto", "title": "➕ Agregar otro"},
        {"id": "btn_finalizar_pedido", "title": "✅ Finalizar pedido"}
    ]
    await send_interactive_buttons(phone=phone, body_text=body_text, buttons=buttons)

async def execute_product_reservation(phone: str, client_name: str, user_state: dict, business_id: int, db: Session):
    user = get_or_create_user(db, phone, business_id, name=client_name.strip())
    productos = user_state.get("productos", [])
    total_price = sum(p["price"] for p in productos)
    names = "\n- ".join(p["name"] for p in productos)
    
    biz = db.query(Business).filter(Business.id == business_id).first()
    horarios = biz.horarios if biz and biz.horarios else "nuestro horario de atención"

    await send_interactive_buttons(
        phone=phone, 
        body_text=f"✅ ¡Pedido Guardado {client_name.strip()}!\n\nTu reserva de:\n{names}\nTotal: ${total_price:,.0f}\n\nEstá asentada. Puedes pasar a retirarlo por el local en {horarios}.",
        buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}]
    )
    log_event(session_id=phone, business_id=business_id, event_type="conversation_closed", payload={"resultado_final": "producto_comprado", "productos": names, "total": total_price})
    await clear_user_state(phone)

# =============================================================================
# CONSULTA, CANCELACIÓN Y FAQ
# =============================================================================

async def handle_view_appointment(phone: str, user_state: dict, business_id: int, db: Session):
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)

    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_interactive_buttons(
            phone=phone, 
            body_text="👀 No tienes turnos próximos agendados.", 
            buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}]
        )
        await clear_user_state(phone)
        return

    upcoming.sort(key=lambda a: a.scheduled_date)

    visits = []
    for appt in upcoming:
        service = db.query(Service).filter(Service.id == appt.service_id).first()
        svc_name = service.name if service else f"Servicio #{appt.service_id}"
        svc_duration = service.duration_minutes if service else 30
        local_dt = appt.scheduled_date.astimezone(tz)

        if visits:
            last_visit = visits[-1]
            if (last_visit["date_str"] == local_dt.strftime("%d/%m/%Y") and
                abs((local_dt - last_visit["end_dt"]).total_seconds()) <= 300):
                last_visit["services"].append(svc_name)
                last_visit["appt_ids"].append(appt.id)
                last_visit["end_dt"] = local_dt + timedelta(minutes=svc_duration)
                last_visit["duration"] += svc_duration
                continue

        visits.append({
            "primary_id": appt.id,
            "appt_ids": [appt.id],
            "client_name": appt.user_name or "Registrado",
            "services": [svc_name],
            "date_str": local_dt.strftime("%d/%m/%Y"),
            "time_str": local_dt.strftime("%H:%M"),
            "start_dt": local_dt,
            "end_dt": local_dt + timedelta(minutes=svc_duration),
            "duration": svc_duration
        })

    primary_visit = visits[0]
    services_str = ", ".join(primary_visit["services"])

    if len(visits) == 1:
        msg = (
            f"👀 *Tu Próximo Turno:*\n\n"
            f"👤 *Cliente:* {primary_visit['client_name']}\n"
            f"💇‍♀️ *Servicio{'s' if len(primary_visit['services']) > 1 else ''}:* {services_str}\n"
            f"📅 *Fecha:* {primary_visit['date_str']}\n"
            f"⏰ *Hora:* {primary_visit['time_str']} hs"
        )
    else:
        msg = f"👀 *Tus Próximos Turnos:*\n\n👤 *Cliente:* {primary_visit['client_name']}\n\n"
        for idx, v in enumerate(visits, 1):
            s_str = ", ".join(v["services"])
            msg += f"{idx}️⃣ *Servicio{'s' if len(v['services']) > 1 else ''}:* {s_str}\n📅 *Fecha:* {v['date_str']}\n⏰ *Hora:* {v['time_str']} hs\n\n"

    await send_interactive_buttons(
        phone=phone, 
        body_text=msg, 
        buttons=[
            {"id": f"btn_mod_appt_{primary_visit['primary_id']}", "title": "🔄 Modificar Turno"},
            {"id": f"btn_confirm_cancel_{primary_visit['primary_id']}", "title": "❌ Cancelar Turno"},
            {"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}
        ]
    )

    await clear_user_state(phone)

async def handle_cancel_appointment_flow(phone: str, user_state: dict, business_id: int, db: Session):
    appointments = get_appointments_by_phone(db, business_id, phone)
    now_tz = datetime.now(timezone.utc)
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)

    upcoming = [a for a in appointments if a.status in ["scheduled", "confirmed"] and a.scheduled_date >= now_tz]

    if not upcoming:
        await send_interactive_buttons(phone=phone, body_text="❌ No tienes turnos activos para cancelar.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
        await clear_user_state(phone)
        return

    upcoming.sort(key=lambda a: a.scheduled_date)

    visits = []
    for appt in upcoming:
        service = db.query(Service).filter(Service.id == appt.service_id).first()
        svc_name = service.name if service else f"Servicio #{appt.service_id}"
        svc_duration = service.duration_minutes if service else 30
        local_dt = appt.scheduled_date.astimezone(tz)

        if visits:
            last_visit = visits[-1]
            if (last_visit["date_str"] == local_dt.strftime("%d/%m/%Y") and
                abs((local_dt - last_visit["end_dt"]).total_seconds()) <= 300):
                last_visit["services"].append(svc_name)
                last_visit["end_dt"] = local_dt + timedelta(minutes=svc_duration)
                continue

        visits.append({
            "primary_id": appt.id,
            "services": [svc_name],
            "date_str": local_dt.strftime("%d/%m/%Y"),
            "time_str": local_dt.strftime("%H:%M"),
            "end_dt": local_dt + timedelta(minutes=svc_duration)
        })

    if len(visits) == 1:
        v = visits[0]
        services_str = ", ".join(v["services"])
        await send_interactive_buttons(
            phone=phone,
            body_text=f"⚠️ *¿Estás seguro de cancelar tu turno?*\n\n💇‍♀️ *Servicio{'s' if len(v['services']) > 1 else ''}:* {services_str}\n📅 *Fecha:* {v['date_str']} a las {v['time_str']} hs",
            buttons=[{"id": f"btn_confirm_cancel_{v['primary_id']}", "title": "SÍ, Cancelar ❌"}, {"id": "btn_volver_menu", "title": "NO, Volver 🔙"}]
        )
    else:
        rows = [
            {
                "id": f"cancel_appt_{v['primary_id']}",
                "title": f"Turno {v['date_str']} {v['time_str']}"[:24],
                "description": f"{', '.join(v['services'])}"[:72]
            }
            for v in visits[:10]
        ]
        await send_interactive_list(
            phone=phone,
            body_text="Tienes varios turnos agendados. Selecciona cuál deseas cancelar:",
            button_label="Ver Turnos 📋",
            sections=[{"title": "Turnos Activos"[:24], "rows": rows}]
        )

async def handle_cancel_confirmation(phone: str, button_id: str, user_state: dict, business_id: int, db: Session):
    if button_id.startswith("btn_confirm_cancel_"):
        try:
            appt_id = int(button_id.replace("btn_confirm_cancel_", ""))
            appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
            if appt:
                tz_str = get_business_timezone(db, business_id)
                tz = zoneinfo.ZoneInfo(tz_str)
                local_dt = appt.scheduled_date.astimezone(tz)
                
                client_appts = get_appointments_by_phone(db, business_id, phone)
                group = [
                    a for a in client_appts
                    if a.status in ["scheduled", "confirmed"]
                    and a.scheduled_date.astimezone(tz).date() == local_dt.date()
                    and abs((a.scheduled_date.astimezone(tz) - local_dt).total_seconds()) < 7200
                ]
                
                for a in group:
                    cancel_appointment(db=db, appointment_id=a.id, business_id=business_id, reason="Cancelado por el cliente")
                    log_event(session_id=phone, business_id=business_id, event_type="appointment_cancelled", payload={"appointment_id": a.id, "reason": "cancelado_por_cliente"})
                    
                await send_interactive_buttons(phone=phone, body_text="✅ Tu turno ha sido cancelado con éxito. El horario fue liberado.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
            else:
                await send_interactive_buttons(phone=phone, body_text="⚠️ Ocurrió un inconveniente al cancelar tu turno.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
        except ValueError:
            await send_interactive_buttons(phone=phone, body_text="Error al procesar la cancelación.", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
        await clear_user_state(phone)

async def handle_faq_selection(phone: str, selected_id: str, row_title: str, user_state: dict, business_id: int, db: Session):
    if selected_id == "btn_hablar_humano":
        await trigger_human_escalation(phone, "Solicitado desde menú FAQ", user_state, business_id, db, reason="faq_human_button")
        return

    biz = db.query(Business).filter(Business.id == business_id).first()
    respuesta_text = ""
    
    if selected_id == "faq_sys_horarios":
        respuesta_text = f"⏰ *Nuestros horarios son:*\n{biz.horarios or 'No especificado'}"
    elif selected_id == "faq_sys_contacto":
        respuesta_text = f"📞 *Puedes contactarnos en:*\n{biz.contacto or 'No especificado'}"
    elif selected_id == "faq_sys_pagos":
        pagos = []
        if biz.accepts_cash: pagos.append("Efectivo")
        if biz.accept_cards: pagos.append("Tarjetas de crédito/débito")
        respuesta_text = f"💳 *Métodos de pago aceptados:*\n{', '.join(pagos) if pagos else 'Consultar en el local'}"
    else:
        faq_id = int(selected_id.replace("faq_", ""))
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            respuesta_text = f"💡 *{faq.question}*\n\n{faq.answer}"
        else:
            respuesta_text = "No se encontró la respuesta."
            
    await send_interactive_buttons(phone=phone, body_text=respuesta_text, buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
    await clear_user_state(phone)

async def handle_faq_query(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    faqs_encontradas = search_faqs(db, business_id, user_text)
    if faqs_encontradas:
        faq = faqs_encontradas[0]
        await send_interactive_buttons(phone=phone, body_text=f"💡 *{faq.question}*\n\n{faq.answer}", buttons=[{"id": "btn_volver_menu", "title": "🔙 Volver al Menú"}])
        await clear_user_state(phone)
    else:
        await trigger_human_escalation(phone, user_text, user_state, business_id, db, reason="faq_not_found")

async def handle_text_fallback(phone: str, user_text: str, user_state: dict, business_id: int, db: Session):
    fallback_n = user_state.get("fallback_count", 0) + 1
    user_state["fallback_count"] = fallback_n

    if fallback_n >= 2:
        await trigger_human_escalation(phone, user_text, user_state, business_id, db, reason="fallback_exceeded")
        return

    await set_user_state(phone, user_state)
    await send_message(phone=phone, text="Por favor selecciona una opción del menú o escribe *Menú* para reiniciar.")

# =============================================================================
# ENRUTADOR PRINCIPAL (WEBHOOK ENDPOINT)
# =============================================================================

@router.get("/webhook")
async def verify_webhook(mode: str = Query(None, alias="hub.mode"), challenge: str = Query(None, alias="hub.challenge"), verify_token: str = Query(None, alias="hub.verify_token")):
    if mode == "subscribe" and verify_token and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=status.HTTP_403_FORBIDDEN)

@router.post("/webhook")
async def receive_webhook(payload: dict, db: Session = Depends(get_db)):
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message = messages[0]
            raw_from = message.get("from")
            phone_number = clean_phone_number(raw_from)
            message_type = message.get("type")

            # -----------------------------------------------------------------
            # 1. ATENCIÓN DE SESIÓN DE CLIENTE BASE
            # -----------------------------------------------------------------
            db_session = db.query(ChatSession).filter(ChatSession.session_id == phone_number).first()
            if not db_session:
                db_session = ChatSession(session_id=phone_number, business_id=MOCK_BUSINESS_ID, user_phone=phone_number, status="active")
                db.add(db_session)
                db.commit()

            current_business_id = db_session.business_id
            user_state = await get_user_state(phone_number) or {}
            current_step = user_state.get("estado", "NUEVO")

            # -----------------------------------------------------------------
            # 2. INTERCEPCIÓN PRIORITARIA DE MENSAJES DEL DUEÑO (PROXY HANDOVER)
            # -----------------------------------------------------------------
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()
                parts = user_text.split(" ", 1)
                if len(parts) >= 1 and parts[0].isdigit():
                    short_id = parts[0]
                    client_phone = await get_client_by_short_id(current_business_id, short_id)
                    if client_phone:
                        # Es un mensaje del dueño para responder o cerrar chat con cliente
                        if len(parts) > 1 and parts[1].strip().lower() == "#fin":
                            await close_human_proxy(current_business_id, short_id)
                            await send_message(phone_number, f"✅ Chat #{short_id} cerrado. Asistente virtual reactivado para el cliente.")
                            await send_interactive_buttons(
                                phone=client_phone,
                                body_text="👨‍💻 El asistente virtual vuelve a estar activo. ¿En qué más puedo ayudarte?",
                                buttons=BOTONES_PRINCIPALES
                            )
                            await clear_user_state(client_phone)
                        else:
                            msg_to_client = parts[1].strip() if len(parts) > 1 else ""
                            if msg_to_client:
                                await send_message(client_phone, msg_to_client)
                        return {"status": "success"}

            # -----------------------------------------------------------------
            # 3. ¿EL CLIENTE ESTÁ EN MODO ATENCIÓN HUMANA?
            # (EL BOT PERMANECE 100% SILENCIOSO. TODO TEXTO SE REENVÍA AL DUEÑO)
            # -----------------------------------------------------------------
            if current_step == "HUMAN_ESCALATION":
                if message_type == "interactive":
                    interactive_data = message.get("interactive", {})
                    if interactive_data.get("type") == "button_reply":
                        selected_id = interactive_data.get("button_reply", {}).get("id")
                        if selected_id in ["btn_volver_menu", "btn_cancelar_humano"]:
                            await handle_welcome_flow(phone_number, current_business_id, db)
                            return {"status": "success"}

                elif message_type == "text":
                    user_text = message.get("text", {}).get("body", "").strip()
                    biz = db.query(Business).filter(Business.id == current_business_id).first()
                    owner_phone = format_phone_for_meta(biz.owner_phone) if biz else None

                    if not owner_phone:
                        await handle_welcome_flow(phone_number, current_business_id, db)
                        return {"status": "success"}

                    short_id = await create_human_proxy(current_business_id, phone_number)
                    known_name = get_existing_user_name(db, phone_number, current_business_id) or phone_number
                    
                    sent_to_owner = await send_message(owner_phone, f"💬 *[#{short_id}] {known_name}:*\n{user_text}")
                    if not sent_to_owner:
                        logger.warning(f"[QA BYPASS] Falló la notificación al dueño ({owner_phone}), pero forzaremos la derivación para testing.")

                return {"status": "success"}

            # -----------------------------------------------------------------
            # 4. MENSAJES DE TEXTO PLANO DEL CLIENTE (O COMANDOS ADMIN/DEMO)
            # -----------------------------------------------------------------
            if message_type == "text":
                user_text = message.get("text", {}).get("body", "").strip()

                # Comandos de reseteo de demo
                if user_text.lower() == "/reset_demo estetica":
                    await _reset_demo_tenant(db, phone_number, 1, "Peluquería")
                    return {"status": "success"}
                elif user_text.lower() == "/reset_demo barberia":
                    await _reset_demo_tenant(db, phone_number, 2, "Barbería")
                    return {"status": "success"}

                # Comando para abrir ventana de 24hs del dueño sin activar menú de cliente
                biz = db.query(Business).filter(Business.id == current_business_id).first()
                owner_phone = format_phone_for_meta(biz.owner_phone) if biz else None

                if owner_phone and is_same_phone(phone_number, owner_phone):
                    if user_text.lower() in ["/activar", "activar", "/admin", "admin"]:
                        await send_message(
                            phone_number, 
                            "👨‍💻 *Modo Administrador*\n\n"
                            "✅ Sesión de 24hs activada. Estás listo para recibir alertas y derivaciones.\n\n"
                            "👉 _Si deseas probar el bot como cliente, escribe_ *Hola*"
                        )
                        return {"status": "success"}

                if any(k in user_text.lower() for k in ["humano", "persona", "agente", "representante", "atencion manual"]):
                    await trigger_human_escalation(phone_number, user_text, user_state, current_business_id, db, reason="keyword_trigger")
                    return {"status": "success"}

                if user_text.lower() in ["hola", "menu", "menú", "volver", "comenzar", "salir", "reiniciar", "cancelar"] or current_step == "NUEVO":
                    await handle_welcome_flow(phone_number, current_business_id, db)
                elif current_step == "ESPERANDO_NOMBRE_TURNO":
                    await execute_appointment_creation(phone_number, user_text, user_state, current_business_id, db)
                elif current_step == "ESPERANDO_NOMBRE_CATALOGO":
                    await execute_product_reservation(phone_number, user_text, user_state, current_business_id, db)
                elif current_step in ["ESPERANDO_FAQ", "SELECCIONANDO_FAQ"]:
                    await handle_faq_query(phone_number, user_text, user_state, current_business_id, db)
                else:
                    await handle_text_fallback(phone_number, user_text, user_state, current_business_id, db)

            # -----------------------------------------------------------------
            # 5. RESPUESTAS INTERACTIVAS (BOTONES Y LISTAS)
            # -----------------------------------------------------------------
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")

                selected_id = None
                row_title = ""
                if interactive_type == "button_reply":
                    selected_id = interactive_data.get("button_reply", {}).get("id")
                elif interactive_type == "list_reply":
                    selected_id = interactive_data.get("list_reply", {}).get("id")
                    row_title = interactive_data.get("list_reply", {}).get("title", "")

                if selected_id:
                    if not is_action_valid_for_state(selected_id, current_step):
                        logger.warning(f"Opción caducada presionada: '{selected_id}' en estado '{current_step}' para {phone_number}")
                        await send_interactive_buttons(
                            phone=phone_number,
                            body_text="⚠️ Esta opción corresponde a un mensaje anterior y ya no está activa. Para comenzar de nuevo, presiona el botón:",
                            buttons=[{"id": "btn_volver_menu", "title": "🔙 Menú Principal"}]
                        )
                        return {"status": "success"}

                    if selected_id == "btn_volver_menu":
                        await handle_welcome_flow(phone_number, current_business_id, db)
                    elif selected_id.startswith("btn_confirm_cancel_"):
                        await handle_cancel_confirmation(phone_number, selected_id, user_state, current_business_id, db)
                    elif selected_id in ["btn_turnos", "btn_catalogo", "btn_faq"]:
                        await handle_main_menu_selection(phone_number, selected_id, user_state, current_business_id, db)
                    elif selected_id.startswith("srv_") or selected_id in ["action_ver_turno", "action_cancelar_turno"]:
                        await handle_service_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id == "btn_agregar_servicio":
                        await handle_main_menu_selection(phone_number, "btn_turnos", user_state, current_business_id, db)
                    elif selected_id == "btn_continuar_fecha":
                        await show_date_selection(phone_number, user_state, current_business_id, db)
                    elif selected_id == "btn_agregar_producto":
                        await handle_main_menu_selection(phone_number, "btn_catalogo", user_state, current_business_id, db)
                    elif selected_id == "btn_finalizar_pedido":
                        known_name = get_existing_user_name(db, phone_number, current_business_id)
                        if known_name:
                            await execute_product_reservation(phone_number, known_name, user_state, current_business_id, db)
                        else:
                            user_state["estado"] = "ESPERANDO_NOMBRE_CATALOGO"
                            await set_user_state(phone_number, user_state)
                            await send_message(phone=phone_number, text=f"Para finalizar tu pedido, escribe tu *Nombre y Apellido* por teclado:")
                    elif selected_id.startswith("date_") or selected_id.startswith("page_slot_"):
                        await handle_date_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("slot_"):
                        await handle_slot_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("prod_"):
                        await handle_product_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("faq_") or selected_id == "btn_hablar_humano":
                        await handle_faq_selection(phone_number, selected_id, row_title, user_state, current_business_id, db)
                    elif selected_id.startswith("cancel_appt_"):
                        try:
                            appt_id = int(selected_id.replace("cancel_appt_", ""))
                            await handle_cancel_confirmation(phone_number, f"btn_confirm_cancel_{appt_id}", user_state, current_business_id, db)
                        except ValueError:
                            await send_message(phone_number, "Error al procesar la lista de cancelación.")
                            await clear_user_state(phone_number)
                    elif selected_id.startswith("btn_mod_appt_") or selected_id.startswith("rem_mod_"):
                        appt_id = int(selected_id.replace("btn_mod_appt_", "").replace("rem_mod_", ""))
                        appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
                        if appt:
                            tz_str = get_business_timezone(db, current_business_id)
                            tz = zoneinfo.ZoneInfo(tz_str)
                            local_dt = appt.scheduled_date.astimezone(tz)
                            
                            # Cancelar todos los servicios pertenecientes a la misma visita/sesión
                            client_appts = get_appointments_by_phone(db, current_business_id, phone_number)
                            group = [
                                a for a in client_appts
                                if a.status in ["scheduled", "confirmed"]
                                and a.scheduled_date.astimezone(tz).date() == local_dt.date()
                                and abs((a.scheduled_date.astimezone(tz) - local_dt).total_seconds()) < 7200
                            ]
                            
                            services_list = []
                            for a in group:
                                svc = db.query(Service).filter(Service.id == a.service_id).first()
                                cancel_appointment(db, a.id, current_business_id, "Modificación solicitada por el cliente")
                                if svc:
                                    services_list.append({
                                        "id": svc.id,
                                        "name": svc.name,
                                        "duration": svc.duration_minutes or 30,
                                        "price": float(svc.price or 0)
                                    })
                            
                            if not services_list:
                                services_list = [{"id": appt.service_id, "name": "Servicio", "duration": 30, "price": 0}]

                            await send_message(phone_number, "Vamos a reprogramar tu turno. Selecciona la nueva fecha:")
                            user_state["servicios"] = services_list
                            await show_date_selection(phone_number, user_state, current_business_id, db)
                    elif selected_id.startswith("rem_conf_"):
                        appt_id = int(selected_id.replace("rem_conf_", ""))
                        appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
                        if appt:
                            appt.no_show_status = "confirmed_yes"
                            db.commit()
                        await send_message(phone_number, "¡Gracias por confirmar! Te esperamos.")
                    elif selected_id.startswith("rem_canc_"):
                        appt_id = int(selected_id.replace("rem_canc_", ""))
                        cancel_appointment(db, appt_id, current_business_id, "Cancelado desde recordatorio")
                        await send_message(phone_number, "Tu turno ha sido cancelado. ¡Gracias por avisar!")

    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")

    return {"status": "success"}