"""Script de seed data inicial para desarrollo y testing.

Crea datos de prueba: negocios, servicios, productos, FAQs y usuarios admin.
Seguro para ejecutar múltiples veces (maneja IntegrityError).

Uso:
    cd repositorio/backend && python -m app.data_seed
"""

import logging

from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models.business import Business
from app.db.models.faq import FAQ
from app.db.models.product import Product
from app.db.models.service import Service
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


def main():
    """Orquesta la creación de seed data: business → services → products → faqs → admin."""
    db = SessionLocal()
    try:
        logger.info("=== Iniciando seed data ===")
        business = seed_business(db)
        seed_services(db, business.id)
        seed_products(db, business.id)
        seed_faqs(db, business.id)
        seed_admin_user(db, business.id)
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
