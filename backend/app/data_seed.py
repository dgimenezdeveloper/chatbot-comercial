"""Script de seed data inicial para desarrollo y testing.

Crea datos de prueba: negocios, servicios, productos, FAQs y usuarios admin.
Seguro para ejecutar múltiples veces (maneja IntegrityError).

Uso:
    cd repositorio/backend && python -m app.data_seed
"""

import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models.business import Business
from app.db.models.events import Event
from app.db.models.faq import FAQ
from app.db.models.feedback import Feedback
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.sessions import ChatSession
from app.db.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_business(db) -> Business:
    """Crea el negocio de prueba si no existe."""
    existing = db.query(Business).filter(Business.slug == "salon-demo-belen").first()
    if existing:
        logger.info("Business ya existe: %s (id=%s)", existing.name, existing.id)
        return existing

    business = Business(
        name="Salon Demo Belén",
        slug="salon-demo-belen",
        description="Peluquería de ejemplo para pruebas y desarrollo del chatbot comercial.",
        active=True,
        timezone="America/Argentina/Buenos_Aires",
        currency="ARS",
        accept_cards=True,
        accepts_cash=True,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    logger.info("Business creado: %s (id=%s)", business.name, business.id)
    return business


def seed_services(db, business_id: int) -> list[Service]:
    """Crea el catálogo inicial de servicios."""
    existing = db.query(Service).filter(Service.business_id == business_id).first()
    if existing:
        logger.info("Servicios ya existen para business_id=%s", business_id)
        return []

    services_data = [
        {"name": "Corte de Cabello", "slug": "corte-cabello", "category": "corte",
         "price": 5000.00, "duration_minutes": 30, "description": "Corte clásico o moderno a elección"},
        {"name": "Tinte de Raíz", "slug": "tinte-raiz", "category": "coloración",
         "price": 8000.00, "duration_minutes": 60, "description": "Tinte profesional para raíz"},
        {"name": "Mechas Californianas", "slug": "mechas-californianas", "category": "coloración",
         "price": 12000.00, "duration_minutes": 120, "description": "Mechas con efecto natural degradado"},
        {"name": "Tratamiento Capilar", "slug": "tratamiento-capilar", "category": "tratamiento",
         "price": 6500.00, "duration_minutes": 45, "description": "Hidratación profunda con keratina"},
        {"name": "Corte de Barba", "slug": "corte-barba", "category": "barba",
         "price": 3500.00, "duration_minutes": 20, "description": "Perfilado y arreglo de barba con toalla caliente"},
        {"name": "Peinado Profesional", "slug": "peinado-profesional", "category": "otros",
         "price": 4000.00, "duration_minutes": 30, "description": "Peinado para eventos con productos premium"},
        {"name": "Alisado Brasileño", "slug": "alisado-brasileno", "category": "tratamiento",
         "price": 15000.00, "duration_minutes": 180, "description": "Alisado sin formol de larga duración"},
        {"name": "Masaje Capilar", "slug": "masaje-capilar", "category": "tratamiento",
         "price": 2500.00, "duration_minutes": 15, "description": "Masaje relajante con aceites esenciales"},
    ]

    services = []
    for data in services_data:
        svc = Service(business_id=business_id, **data)
        db.add(svc)
        services.append(svc)
    db.commit()
    logger.info("Creados %s servicios para business_id=%s", len(services), business_id)
    return services


def seed_products(db, business_id: int) -> list[Product]:
    """Crea productos de venta iniciales."""
    existing = db.query(Product).filter(Product.business_id == business_id).first()
    if existing:
        logger.info("Productos ya existen para business_id=%s", business_id)
        return []

    products_data = [
        {"name": "Shampoo Profesional 300ml", "slug": "shampoo-profesional",
         "price": 3500.00, "cost_price": 2000.00, "stock_quantity": 20,
         "description": "Shampoo anticaída con extracto de ortiga"},
        {"name": "Acondicionador Nutritivo 300ml", "slug": "acondicionador-nutritivo",
         "price": 3200.00, "cost_price": 1800.00, "stock_quantity": 15,
         "description": "Acondicionador con aceite de argán"},
        {"name": "Serum Capilar Reparador", "slug": "serum-capilar",
         "price": 2800.00, "cost_price": 1500.00, "stock_quantity": 10,
         "description": "Serum de puntas abiertas con vitamina E"},
        {"name": "Cera Modeladora Matte", "slug": "cera-modeladora",
         "price": 3200.00, "cost_price": 1700.00, "stock_quantity": 25,
         "description": "Cera de fijación fuerte con efecto seco"},
    ]

    products = []
    for data in products_data:
        prod = Product(business_id=business_id, **data)
        db.add(prod)
        products.append(prod)
    db.commit()
    logger.info("Creados %s productos para business_id=%s", len(products), business_id)
    return products


def seed_faqs(db, business_id: int) -> list[FAQ]:
    """Crea preguntas frecuentes iniciales."""
    existing = db.query(FAQ).filter(FAQ.business_id == business_id).first()
    if existing:
        logger.info("FAQs ya existen para business_id=%s", business_id)
        return []

    faqs_data = [
        {"question": "¿Cómo agendo un turno?", "answer": "Escribinos 'Hola' y seguí el menú interactivo. Elegí 'Turnos', seleccioná el servicio, la fecha y horario que prefieras.", "category": "turnos", "order": 1},
        {"question": "¿Cuáles son los precios?", "answer": "Los precios varían según el servicio. Corte $5000, Tinte $8000, Mechas $12000, Tratamiento $6500. Consultá el catálogo completo en el menú.", "category": "precios", "order": 2},
        {"question": "¿Puedo cancelar un turno?", "answer": "Sí, podés cancelar con al menos 24hs de anticipación sin costo. Escribí 'Cancelar turno' en el menú de Turnos.", "category": "turnos", "order": 3},
        {"question": "¿Cuáles son los horarios?", "answer": "Atendemos de Lunes a Sábados de 09:00 a 20:00hs. Domingos cerrado.", "category": "horarios", "order": 4},
        {"question": "¿Qué métodos de pago aceptan?", "answer": "Aceptamos efectivo, tarjetas de crédito y débito (Visa, Mastercard), y MercadoPago.", "category": "pagos", "order": 5},
        {"question": "¿Dónde están ubicados?", "answer": "Nos encontramos en Av. Principal 123, Ciudad. A dos cuadras de la estación de tren.", "category": "ubicacion", "order": 6},
    ]

    faqs = []
    for data in faqs_data:
        faq = FAQ(business_id=business_id, **data)
        db.add(faq)
        faqs.append(faq)
    db.commit()
    logger.info("Creadas %s FAQs para business_id=%s", len(faqs), business_id)
    return faqs


def seed_admin_user(db, business_id: int) -> User:
    """Crea un usuario administrador para el negocio."""
    existing = db.query(User).filter(
        User.business_id == business_id, User.role == "admin"
    ).first()
    if existing:
        logger.info("Admin user ya existe: %s (id=%s)", existing.email, existing.id)
        return existing

    user = User(
        business_id=business_id,
        name="Administrador Demo",
        email="admin@salondemo.com",
        phone="5491123456789",
        role="admin",
        is_active=True,
        can_manage_appointments=True,
        can_view_analytics=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Admin user creado: %s (id=%s)", user.email, user.id)
    return user


def seed_sessions(db, business_id: int, user: User) -> list[ChatSession]:
    """Crea sesiones de ejemplo con estados y métricas variadas."""
    existing = db.query(ChatSession).filter(ChatSession.business_id == business_id).first()
    if existing:
        logger.info("Sesiones ya existen para business_id=%s", business_id)
        return db.query(ChatSession).filter(ChatSession.business_id == business_id).all()

    now = datetime.now(timezone.utc)
    sessions_data = [
        {"session_id": f"wa-session-{business_id}-001", "status": "completed",
         "n_messages_total": 8, "n_fallbacks": 0, "days_ago": 0},
        {"session_id": f"wa-session-{business_id}-002", "status": "completed",
         "n_messages_total": 12, "n_fallbacks": 1, "days_ago": 0},
        {"session_id": f"wa-session-{business_id}-003", "status": "completed",
         "n_messages_total": 5, "n_fallbacks": 0, "days_ago": 1},
        {"session_id": f"wa-session-{business_id}-004", "status": "abandoned",
         "n_messages_total": 3, "n_fallbacks": 2, "days_ago": 1},
        {"session_id": f"wa-session-{business_id}-005", "status": "completed",
         "n_messages_total": 15, "n_fallbacks": 3, "days_ago": 1},
        {"session_id": f"wa-session-{business_id}-006", "status": "active",
         "n_messages_total": 4, "n_fallbacks": 0, "days_ago": 0},
        {"session_id": f"wa-session-{business_id}-007", "status": "completed",
         "n_messages_total": 10, "n_fallbacks": 0, "days_ago": 2},
        {"session_id": f"wa-session-{business_id}-008", "status": "completed",
         "n_messages_total": 7, "n_fallbacks": 1, "days_ago": 2},
    ]

    sessions = []
    for sd in sessions_data:
        started_at = now - timedelta(days=sd["days_ago"], hours=random.randint(0, 12))
        ended_at = started_at + timedelta(minutes=random.randint(3, 25)) if sd["status"] != "active" else None
        session = ChatSession(
            business_id=business_id,
            session_id=sd["session_id"],
            user_id=user.id,
            user_phone=user.phone,
            status=sd["status"],
            n_messages_total=sd["n_messages_total"],
            n_fallbacks=sd["n_fallbacks"],
            started_at=started_at,
            ended_at=ended_at,
        )
        db.add(session)
        sessions.append(session)

    try:
        db.commit()
        logger.info("Creadas %s sesiones para business_id=%s", len(sessions), business_id)
    except IntegrityError:
        db.rollback()
        logger.warning("Sesiones ya existentes (IntegrityError), se retornan las existentes")
        return db.query(ChatSession).filter(ChatSession.business_id == business_id).all()

    return sessions


def seed_events(db, business_id: int, sessions: list[ChatSession]) -> list[Event]:
    """Crea eventos instrumentados para las sesiones de ejemplo."""
    existing = db.query(Event).filter(Event.business_id == business_id).first()
    if existing:
        logger.info("Eventos ya existen para business_id=%s", business_id)
        return []

    event_types_ordered = [
        "conversation_started",
        "menu_option_selected",
        "service_selected",
        "appointment_created",
        "reminder_sent",
        "reminder_response",
        "conversation_closed",
    ]

    sample_payloads = {
        "conversation_started": {"is_new_user": True, "channel": "whatsapp"},
        "menu_option_selected": {"option_name": "btn_turnos"},
        "service_selected": {"service_id": "srv_corte", "service_name": "Corte de Cabello"},
        "appointment_created": {"via_bot": True, "servicio": "Corte de Cabello", "fecha": "Hoy", "hora": "10:00 hs"},
        "reminder_sent": {"servicio": "Corte de Cabello", "fecha": "Hoy", "hora": "10:00 hs"},
        "reminder_response": {"response_type": "confirmo", "appointment_id": 1},
        "conversation_closed": {"resultado_final": "turno_creado", "n_fallbacks": 0},
    }

    events = []
    for session in sessions:
        if session.status == "active":
            # Solo conversation_started + menu_option_selected para sesiones activas
            for et in ["conversation_started", "menu_option_selected"]:
                event = Event(
                    session_id=session.session_id,
                    business_id=business_id,
                    event_type=et,
                    payload_json=sample_payloads.get(et),
                    timestamp=session.started_at + timedelta(seconds=random.randint(1, 60)),
                    user_id=session.user_id,
                    channel="whatsapp",
                )
                db.add(event)
                events.append(event)
        else:
            # Secuencia completa para sesiones completadas/abandonadas
            base_time = session.started_at
            for i, et in enumerate(event_types_ordered):
                # Sesiones abandonadas: solo llegan hasta fallback
                if session.status == "abandoned" and et in ("appointment_created", "reminder_sent", "reminder_response"):
                    # Agregar fallback_triggered en lugar de eventos transaccionales
                    if et == "appointment_created":
                        fb_event = Event(
                            session_id=session.session_id,
                            business_id=business_id,
                            event_type="fallback_triggered",
                            payload_json={"message_original": "texto de prueba", "fallback_n": 1},
                            timestamp=base_time + timedelta(seconds=random.randint(30, 90)),
                            user_id=session.user_id,
                            channel="whatsapp",
                        )
                        db.add(fb_event)
                        events.append(fb_event)
                    continue

                event = Event(
                    session_id=session.session_id,
                    business_id=business_id,
                    event_type=et,
                    payload_json=sample_payloads.get(et),
                    timestamp=base_time + timedelta(seconds=random.randint(10, 120) + i * 30),
                    user_id=session.user_id,
                    channel="whatsapp",
                )
                db.add(event)
                events.append(event)

            # Agregar escalation_to_human a algunas sesiones con fallbacks
            if session.n_fallbacks >= 2:
                esc_event = Event(
                    session_id=session.session_id,
                    business_id=business_id,
                    event_type="escalation_to_human",
                    payload_json={"reason": "fallback_exceeded", "n_fallbacks_previos": session.n_fallbacks},
                    timestamp=base_time + timedelta(minutes=random.randint(3, 8)),
                    user_id=session.user_id,
                    channel="whatsapp",
                )
                db.add(esc_event)
                events.append(esc_event)

    try:
        db.commit()
        logger.info("Creados %s eventos para business_id=%s", len(events), business_id)
    except IntegrityError:
        db.rollback()
        logger.warning("Eventos ya existentes (IntegrityError), se retornan los existentes")
        return db.query(Event).filter(Event.business_id == business_id).all()

    return events


def seed_feedback(db, business_id: int, sessions: list[ChatSession]) -> list[Feedback]:
    """Crea feedbacks CSAT de ejemplo con scores y outcomes variados."""
    existing = db.query(Feedback).filter(Feedback.business_id == business_id).first()
    if existing:
        logger.info("Feedbacks ya existen para business_id=%s", business_id)
        return []

    completed_sessions = [s for s in sessions if s.status == "completed"]
    if not completed_sessions:
        logger.info("Sin sesiones completadas, no se crean feedbacks")
        return []

    feedbacks_data = [
        {"score": 5, "outcome": "turno_exitoso", "comment": "¡Excelente atención, muy rápido!"},
        {"score": 4, "outcome": "turno_exitoso", "comment": "Muy buen servicio, aunque tuve que esperar un poco."},
        {"score": 5, "outcome": "turno_exitoso", "comment": "Me encantó el chatbot, súper fácil de usar."},
        {"score": 3, "outcome": "escalado_exitoso", "comment": "Tuve un problema pero me ayudaron rápido."},
        {"score": 5, "outcome": "turno_exitoso", "comment": None},
    ]

    feedbacks = []
    now = datetime.now(timezone.utc)
    for i, fd in enumerate(feedbacks_data):
        if i >= len(completed_sessions):
            break
        session = completed_sessions[i]
        feedback = Feedback(
            business_id=business_id,
            session_id=session.session_id,
            score=fd["score"],
            outcome=fd["outcome"],
            comment=fd["comment"],
            submitted_at=session.ended_at or now,
            user_phone=session.user_phone,
        )
        db.add(feedback)
        feedbacks.append(feedback)

    try:
        db.commit()
        logger.info("Creados %s feedbacks para business_id=%s", len(feedbacks), business_id)
    except IntegrityError:
        db.rollback()
        logger.warning("Feedbacks ya existentes (IntegrityError), se retornan los existentes")
        return db.query(Feedback).filter(Feedback.business_id == business_id).all()

    return feedbacks


def seed_metric_thresholds(db) -> list:
    """Inserta los thresholds defaults del sistema (business_id=NULL)."""
    from app.db.models.metric_threshold import MetricThreshold

    defaults = [
        {"metric_name": "conversion_rate", "warning_value": 0.20, "critical_value": 0.10, "operator": "lt"},
        {"metric_name": "bot_autonomy_rate", "warning_value": 0.40, "critical_value": 0.25, "operator": "lt"},
        {"metric_name": "abandonment_rate", "warning_value": 0.30, "critical_value": 0.40, "operator": "gt"},
        {"metric_name": "fallback_rate", "warning_value": 0.15, "critical_value": 0.25, "operator": "gt"},
        {"metric_name": "nocturnal_appointment_rate", "warning_value": 0.10, "critical_value": 0.30, "operator": "gt"},
        {"metric_name": "autonomous_resolution_rate", "warning_value": 0.70, "critical_value": 0.50, "operator": "lt"},
        {"metric_name": "cancellation_rate", "warning_value": 0.15, "critical_value": 0.20, "operator": "gt"},
        {"metric_name": "no_show_rate", "warning_value": 0.10, "critical_value": 0.15, "operator": "gt"},
        {"metric_name": "reminder_confirmation_rate", "warning_value": 0.60, "critical_value": 0.50, "operator": "lt"},
        {"metric_name": "csat_average", "warning_value": 4.0, "critical_value": 3.5, "operator": "lt"},
        {"metric_name": "reminder_delivery_rate", "warning_value": 0.90, "critical_value": 0.75, "operator": "lt"},
        {"metric_name": "manual_escalation_rate", "warning_value": 0.30, "critical_value": 0.50, "operator": "gt"},
        {"metric_name": "nps", "warning_value": 50.0, "critical_value": 0.0, "operator": "lt"},
    ]

    existing = db.query(MetricThreshold).filter(MetricThreshold.business_id.is_(None)).count()
    if existing > 0:
        logger.info("Thresholds defaults ya existen (%s registros)", existing)
        return db.query(MetricThreshold).filter(MetricThreshold.business_id.is_(None)).all()

    thresholds = []
    for item in defaults:
        t = MetricThreshold(
            business_id=None,
            metric_name=item["metric_name"],
            warning_value=item["warning_value"],
            critical_value=item["critical_value"],
            operator=item["operator"],
        )
        db.add(t)
        thresholds.append(t)

    db.commit()
    logger.info("Creados %s thresholds defaults del sistema", len(thresholds))
    return thresholds


def main():
    """Orquesta la creación de seed data: business → services → products → faqs → admin → sessions → events → feedback → thresholds."""
    db = SessionLocal()
    try:
        logger.info("=== Iniciando seed data ===")
        business = seed_business(db)
        # Configurar default: sin templates pagos + owner_phone
        if not business.owner_phone:
            business.owner_phone = "+5491112345678"
        if business.use_whatsapp_templates is None:
            business.use_whatsapp_templates = False
        user = seed_admin_user(db, business.id)
        seed_services(db, business.id)
        seed_products(db, business.id)
        seed_faqs(db, business.id)
        sessions = seed_sessions(db, business.id, user)
        seed_events(db, business.id, sessions)
        seed_feedback(db, business.id, sessions)
        seed_metric_thresholds(db)
        db.commit()
        logger.info("=== Seed data completado ===")
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError (posible duplicado): %s", e)
    except Exception:
        db.rollback()
        logger.exception("Error inesperado durante seed data")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
