"""Script de seed data — modo básico y modo enriquecido.

Modo básico (default): Crea datos de prueba: negocios (1 y 2), usuarios de la lista blanca,
    servicios, productos, FAQs y thresholds.
    Seguro para ejecutar múltiples veces (idempotente).

Modo enriquecido (--enriched): Genera 30 días de datos realistas (~500 conversaciones,
    ~350 turnos, ~60 fallbacks, ~50 feedbacks, ~100 recordatorios) para probar TODAS
    las métricas del dashboard. TRUNCA tablas transaccionales antes de insertar.

Uso:
    cd repositorio/backend
    python -m app.data_seed              # Modo básico (idempotente)
    python -m app.data_seed --enriched   # Modo enriquecido (destructivo)
"""

import logging
import random
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_
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
from app.db.models.appointment import Appointment
from app.db.models.reminder_log import ReminderLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

random.seed(42)
NOW = datetime.now(timezone.utc)

# Lista blanca oficial del Equipo 10 -> Inquilino 1 (Peluquería)
TEAM_MEMBERS_BUSINESS_1 = [
    ("Dario Sebastian Gimenez", "dgimenez.developer@gmail.com"),
    ("Darle Miguel Sanabria", "sanajani410@gmail.com"),
    ("Aleska Cegarra", "cegarraaleska91@gmail.com"),
    ("Manfred Camacho", "manfred.camacho.dev@gmail.com"),
    ("Arlene Rojas", "arleni1108@gmail.com"),
    ("Veronica Ledezma", "chibi.viky@gmail.com"),
    ("Feliangela Garcia", "fgfscg@gmail.com"),
    ("Dana Stornello", "stornellodana@gmail.com"),
    ("Yanina Nabel", "yaninanabel@hotmail.com"),
    ("Ariadna Arias", "ariasari.7066@gmail.com"),
    ("Matias Joaquin Lobos", "matiasjoaquinlobos@gmail.com"),
    ("Victor Villamizar", "vmvillamar@gmail.com"),
    ("Roberto Rossa", "roberto.carlo.rossa@gmail.com"),
    ("Gaspar Nicolás Martínez", "gnmartinez214@gmail.com"),
    ("Janneth Chura", "janneth.chura@bue.edu.ar"),
]

FALLBACK_MESSAGES = [
    "cual es el precio del corte",
    "puedo ir manana a las 8",
    "que servicios tienen",
    "me atiende juan",
    "tienen descuento por primera vez",
    "hacen pago con mercado pago",
    "esta disponible el sabado",
    "cuanto dura el alisado",
    "cobran con tarjeta de credito",
    "hay turno para hoy a la tarde",
]

CSAT_COMMENTS = [
    "¡Excelente atención!", "Muy rápido el proceso", "Me encantó el chatbot",
    "Tuve que esperar un poco", "El bot no entendió mi consulta", None,
    "Súper fácil de usar", "Buen servicio", "Regular, mejoró con humano",
    "No me gustó la demora", "Perfecto todo",
]

# =====================================================================
# MODO BÁSICO — Funciones idempotentes
# =====================================================================

def seed_businesses(db) -> tuple[Business, Business]:
    """Crea los negocios de la demo si no existen."""
    b1 = db.query(Business).filter(Business.id == 1).first()
    if not b1:
        b1 = Business(
            id=1,
            name="Salon Demo Belén",
            slug="salon-demo-belen",
            description="Peluquería de ejemplo para pruebas y desarrollo del chatbot comercial.",
            active=True,
            timezone="America/Argentina/Buenos_Aires",
            currency="ARS",
            accept_cards=True,
            accepts_cash=True,
            owner_phone="+5491112345678",
        )
        db.add(b1)
        db.commit()
        db.refresh(b1)
        logger.info("Business 1 creado: %s (id=1)", b1.name)

    b2 = db.query(Business).filter(Business.id == 2).first()
    if not b2:
        b2 = Business(
            id=2,
            name="Barbería Innova",
            slug="barberia-innova",
            description="Barbería moderna y de vanguardia para demostración de nuevo cliente SaaS.",
            active=True,
            timezone="America/Argentina/Buenos_Aires",
            currency="ARS",
            accept_cards=True,
            accepts_cash=True,
            owner_phone="+5491199998888",
        )
        db.add(b2)
        db.commit()
        db.refresh(b2)
        logger.info("Business 2 creado: %s (id=2)", b2.name)

    return b1, b2


def seed_admin_users(db, b1_id: int, b2_id: int):
    """Siembra los usuarios autorizados de la lista blanca en la DB."""
    # 1. Miembros del Equipo -> Inquilino 1 (Peluquería)
    for name, email in TEAM_MEMBERS_BUSINESS_1:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                business_id=b1_id,
                name=name,
                email=email,
                role="admin",
                is_active=True,
                can_manage_appointments=True,
                can_view_analytics=True,
                oauth_provider="google",
            )
            db.add(user)
            logger.info("Usuario Lista Blanca 1 creado: %s (%s)", name, email)

    # 2. Admin Barbería -> Inquilino 2 (Barbería)
    u2 = db.query(User).filter(User.email == "barberia.demo26@gmail.com").first()
    if not u2:
        u2 = User(
            business_id=b2_id,
            name="Barbería Admin",
            email="barberia.demo26@gmail.com",
            role="admin",
            is_active=True,
            can_manage_appointments=True,
            can_view_analytics=True,
            oauth_provider="google",
        )
        db.add(u2)
        logger.info("Usuario Lista Blanca 2 creado: barberia.demo26@gmail.com")

    db.commit()


def seed_services(db, business_id: int) -> list[Service]:
    """Crea el catálogo inicial de servicios solo para Business 1."""
    if business_id != 1:
        return []

    existing = db.query(Service).filter(Service.business_id == business_id).first()
    if existing:
        logger.info("Servicios ya existen para business_id=%s", business_id)
        return db.query(Service).filter(Service.business_id == business_id).all()

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
    """Crea productos de venta iniciales solo para Business 1."""
    if business_id != 1:
        return []

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
    """Crea preguntas frecuentes solo para Business 1."""
    if business_id != 1:
        return []

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


def run_basic_seed(db):
    """Orquesta la creación de seed data básica e idempotente."""
    logger.info("=== Seed BÁSICO ===")
    b1, b2 = seed_businesses(db)
    seed_admin_users(db, b1.id, b2.id)
    seed_services(db, b1.id)
    seed_products(db, b1.id)
    seed_faqs(db, b1.id)
    seed_metric_thresholds(db)
    db.commit()
    logger.info("=== Seed BÁSICO completado ===")
    return b1, b2


# =====================================================================
# MODO ENRIQUECIDO — Datos transaccionales para Business 1
# =====================================================================

def truncate_transactional_tables(db):
    """Limpia todas las tablas de datos transaccionales preservando schema."""
    tables = [Event, Feedback, ReminderLog, ChatSession, Appointment]
    for table in tables:
        db.execute(table.__table__.delete())
    db.commit()
    logger.info("Tablas truncadas: events, feedbacks, reminder_logs, sessions, appointments")


def generate_random_date(days_ago: int) -> datetime:
    """Genera un timestamp aleatorio en un día específico del pasado."""
    base = NOW - timedelta(days=days_ago)
    hour = random.randint(7, 22)
    minute = random.randint(0, 59)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def generate_sessions(db, business_id: int, user: User, count: int = 500) -> list[ChatSession]:
    """Genera sesiones de conversación con distribución realista de estados."""
    sessions = []
    for i in range(count):
        days_ago = random.randint(0, 29)
        started = generate_random_date(days_ago)

        r = random.random()
        if r < 0.65:
            status = "completed"
            duration = random.randint(3, 25)
            n_messages = random.randint(5, 20)
            n_fallbacks = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
        elif r < 0.85:
            status = "abandoned"
            duration = random.randint(1, 8)
            n_messages = random.randint(2, 5)
            n_fallbacks = random.choices([0, 1, 2, 3], weights=[20, 40, 30, 10])[0]
        else:
            status = "active"
            days_ago = random.randint(0, 1)
            started = generate_random_date(days_ago)
            duration = None
            n_messages = random.randint(2, 6)
            n_fallbacks = 0

        ended = started + timedelta(minutes=duration) if duration else None

        s = ChatSession(
            business_id=business_id,
            session_id=f"wa-enriched-{business_id}-{i:04d}",
            user_id=user.id if user else None,
            user_phone=f"54911{random.randint(20000000, 99999999)}",
            status=status,
            n_messages_total=n_messages,
            n_fallbacks=n_fallbacks,
            started_at=started,
            ended_at=ended,
        )
        db.add(s)
        sessions.append(s)

    db.commit()
    logger.info("Creadas %d sesiones enriquecidas", len(sessions))
    return sessions


def generate_events(db, business_id: int, sessions: list[ChatSession]) -> list[Event]:
    """Genera eventos instrumentados para cada sesión con datos realistas."""
    events = []
    service_ids = list(range(1, 9))

    for session in sessions:
        t = session.started_at
        sid = session.session_id
        uid = session.user_id

        events.append(Event(session_id=sid, business_id=business_id,
                            event_type="conversation_started",
                            payload_json={"is_new_user": random.random() > 0.4, "channel": "whatsapp"},
                            timestamp=t, user_id=uid, channel="whatsapp"))

        events.append(Event(session_id=sid, business_id=business_id,
                            event_type="menu_option_selected",
                            payload_json={"option_name": random.choice(["btn_turnos", "btn_precios", "btn_faq"])},
                            timestamp=t + timedelta(seconds=random.randint(5, 30)),
                            user_id=uid, channel="whatsapp"))

        if session.status != "abandoned" or random.random() > 0.3:
            svc_id = random.choice(service_ids)
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="service_selected",
                                payload_json={"service_id": svc_id, "confidence_score": random.uniform(0.7, 1.0)},
                                timestamp=t + timedelta(seconds=random.randint(30, 90)),
                                user_id=uid, channel="whatsapp"))

        for fb_n in range(session.n_fallbacks):
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="fallback_triggered",
                                payload_json={
                                    "message_original": random.choice(FALLBACK_MESSAGES),
                                    "fallback_n": fb_n + 1,
                                    "previous_state": "service_selection",
                                },
                                timestamp=t + timedelta(seconds=random.randint(60, 180)),
                                user_id=uid, channel="whatsapp"))

        if session.n_fallbacks >= 2 or (session.status == "abandoned" and random.random() > 0.5):
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="escalation_to_human",
                                payload_json={
                                    "reason": "fallback_exceeded" if session.n_fallbacks >= 2 else "user_request",
                                    "n_fallbacks_previos": session.n_fallbacks,
                                },
                                timestamp=t + timedelta(seconds=random.randint(120, 300)),
                                user_id=uid, channel="whatsapp"))

        if session.status == "completed" and random.random() > 0.15:
            hour = t.hour + random.randint(0, 3)
            nocturnal = hour >= 20 or hour < 8
            svc_id = random.choice(service_ids)
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="appointment_created",
                                payload_json={
                                    "appointment_id": f"appt-{sid}",
                                    "via_bot": True,
                                    "horario_nocturno": nocturnal,
                                    "service_id": svc_id,
                                },
                                timestamp=t + timedelta(seconds=random.randint(90, 240)),
                                user_id=uid, channel="whatsapp"))

            reminder_time = t + timedelta(hours=random.randint(20, 28))
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="reminder_sent",
                                payload_json={"appointment_id": f"appt-{sid}", "channel": "whatsapp"},
                                timestamp=reminder_time,
                                user_id=uid, channel="whatsapp"))

            if random.random() > 0.3:
                resp = random.choices(["confirmo", "cancelo", "cambio"], weights=[65, 25, 10])[0]
                events.append(Event(session_id=sid, business_id=business_id,
                                    event_type="reminder_response",
                                    payload_json={"response_type": resp, "appointment_id": f"appt-{sid}"},
                                    timestamp=reminder_time + timedelta(minutes=random.randint(1, 120)),
                                    user_id=uid, channel="whatsapp"))

        if session.status == "completed" and random.random() > 0.4:
            score = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="csat_submitted",
                                payload_json={"score": score, "outcome": "turno_exitoso" if random.random() > 0.2 else "escalado_exitoso"},
                                timestamp=t + timedelta(seconds=random.randint(180, 600)),
                                user_id=uid, channel="whatsapp"))

        if session.status in ("completed", "abandoned"):
            events.append(Event(session_id=sid, business_id=business_id,
                                event_type="conversation_closed",
                                payload_json={
                                    "duracion_seg": random.randint(30, 900),
                                    "n_mensajes": session.n_messages_total,
                                    "n_fallbacks": session.n_fallbacks,
                                    "resultado_final": "turno_creado" if session.status == "completed" else "abandonado",
                                },
                                timestamp=session.ended_at or t + timedelta(minutes=10),
                                user_id=uid, channel="whatsapp"))

    db.bulk_save_objects(events)
    db.commit()
    logger.info("Creados %d eventos enriquecidos", len(events))
    return events


def generate_appointments(db, business_id: int, user: User, services: list[Service]) -> list[Appointment]:
    """Crea turnos reales en la tabla appointment con distribución realista."""
    appointments = []
    service_ids = [s.id for s in services] if services else [1]

    def random_hour(nocturnal):
        if nocturnal:
            return random.choice(list(range(0, 8)) + list(range(20, 24)))
        return random.randint(8, 19)

    for _ in range(200):
        days_ago = random.randint(0, 29)
        nocturnal = random.random() < 0.4
        hour = random_hour(nocturnal)
        scheduled = NOW - timedelta(days=days_ago)
        scheduled = scheduled.replace(hour=hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)

        status = random.choices(["scheduled", "confirmed", "completed", "cancelled"], weights=[5, 10, 70, 15])[0]
        no_show = None
        if status == "completed" and random.random() < 0.1:
            no_show = "confirmed_no"
        elif status == "completed":
            no_show = "confirmed_yes"

        created_via = random.choices(["chatbot", "web"], weights=[85, 15])[0]

        a = Appointment(
            business_id=business_id,
            user_id=user.id if user else None,
            user_phone=f"54911{random.randint(20000000, 99999999)}",
            user_name=f"Cliente {random.randint(1, 500)}",
            service_id=random.choice(service_ids),
            scheduled_date=scheduled,
            status=status,
            no_show_status=no_show,
            created_via=created_via,
            session_id=f"wa-enriched-{business_id}-{random.randint(0, 499):04d}",
            created_at=scheduled - timedelta(days=random.randint(1, 7)),
        )
        db.add(a)
        appointments.append(a)

    for _ in range(80):
        days_ahead = random.randint(0, 13)
        nocturnal = random.random() < 0.4
        hour = random_hour(nocturnal)
        scheduled = NOW + timedelta(days=days_ahead)
        scheduled = scheduled.replace(hour=hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)

        a = Appointment(
            business_id=business_id,
            user_id=user.id if user else None,
            user_phone=f"54911{random.randint(20000000, 99999999)}",
            user_name=f"Cliente Futuro {random.randint(1, 100)}",
            service_id=random.choice(service_ids),
            scheduled_date=scheduled,
            status=random.choices(["scheduled", "confirmed"], weights=[30, 70])[0],
            no_show_status=None,
            created_via=random.choices(["chatbot", "web"], weights=[80, 20])[0],
            session_id=f"wa-enriched-{business_id}-{random.randint(0, 499):04d}",
            created_at=NOW - timedelta(hours=random.randint(1, 48)),
        )
        db.add(a)
        appointments.append(a)

    db.commit()
    logger.info("Creados %d turnos enriquecidos", len(appointments))
    return appointments


def generate_feedbacks(db, business_id: int, sessions: list[ChatSession]) -> list[Feedback]:
    """Genera feedbacks CSAT para sesiones completadas."""
    completed = [s for s in sessions if s.status == "completed"]
    feedbacks = []
    for s in completed[:150]:
        if random.random() > 0.6:
            continue
        score = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
        f = Feedback(
            business_id=business_id,
            session_id=s.session_id,
            score=score,
            outcome=random.choice(["turno_exitoso", "escalado_exitoso", "abandonado"]),
            comment=random.choice(CSAT_COMMENTS),
            submitted_at=s.ended_at or NOW,
            user_phone=s.user_phone,
        )
        db.add(f)
        feedbacks.append(f)
    db.commit()
    logger.info("Creados %d feedbacks enriquecidos", len(feedbacks))
    return feedbacks


def generate_reminder_logs(db, business_id: int, sessions: list[ChatSession]) -> list[ReminderLog]:
    """Genera reminder_logs con estados variados."""
    completed = [s for s in sessions if s.status == "completed"]
    logs = []
    for s in completed[:200]:
        if random.random() > 0.7:
            continue
        rl = ReminderLog(
            business_id=business_id,
            appointment_id=None,
            status=random.choices(["sent", "failed", "outside_window", "fallback_channel"], weights=[70, 10, 10, 10])[0],
            channel=random.choices(["whatsapp_text", "whatsapp_template", "sms", "email"], weights=[80, 10, 5, 5])[0],
            sent_at=s.ended_at or NOW,
            error_reason="Timeout de conexión" if random.random() < 0.1 else None,
        )
        db.add(rl)
        logs.append(rl)
    db.commit()
    logger.info("Creados %d reminder_logs enriquecidos", len(logs))
    return logs


def run_enriched_seed(db):
    """Orquesta la creación de seed data enriquecida (trunca datos transaccionales primero)."""
    logger.info("=== Seed ENRIQUECIDO — Inicio ===")
    truncate_transactional_tables(db)
    b1, b2 = seed_businesses(db)
    seed_admin_users(db, b1.id, b2.id)
    services = seed_services(db, b1.id)
    seed_products(db, b1.id)
    seed_faqs(db, b1.id)
    seed_metric_thresholds(db)

    admin_b1 = db.query(User).filter(User.business_id == b1.id).first()
    sessions = generate_sessions(db, b1.id, admin_b1, count=500)
    generate_events(db, b1.id, sessions)
    generate_appointments(db, b1.id, admin_b1, services)
    generate_feedbacks(db, b1.id, sessions)
    generate_reminder_logs(db, b1.id, sessions)
    logger.info("=== Seed ENRIQUECIDO — Completado ===")


def main():
    db = SessionLocal()
    try:
        if "--enriched" in sys.argv:
            run_enriched_seed(db)
        else:
            run_basic_seed(db)
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError durante seed: %s", e)
    except Exception:
        db.rollback()
        logger.exception("Error inesperado durante seed data")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()