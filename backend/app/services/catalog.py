"""Servicio CRUD para catálogo — productos y servicios.

Operaciones contra PostgreSQL usando SQLAlchemy Session.
Reemplaza los mocks de los endpoints de catalog.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.product import Product
from app.db.models.service import Service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Whitelists de campos actualizables — evitan sobrescritura de id, business_id,
# created_at y atributos inexistentes.
# ---------------------------------------------------------------------------

SERVICE_ALLOWED_FIELDS = {
    'name', 'slug', 'description', 'category', 'subcategory',
    'price', 'duration_minutes', 'slots_available_per_day',
    'is_active', 'requires_stock', 'stock_quantity', 'image_url', 'updated_at',
}

PRODUCT_ALLOWED_FIELDS = {
    'name', 'slug', 'description', 'price', 'cost_price',
    'stock_quantity', 'low_stock_threshold', 'is_active', 'image_url', 'updated_at',
}


# ---------------------------------------------------------------------------
# Servicios
# ---------------------------------------------------------------------------

def get_services(db: Session, business_id: int) -> list[Service]:
    """Lista todos los servicios activos de un negocio."""
    return (
        db.query(Service)
        .filter(Service.business_id == business_id, Service.is_active.is_(True))
        .order_by(Service.category, Service.name)
        .all()
    )


def get_service(db: Session, service_id: int, business_id: int) -> Optional[Service]:
    """Obtiene un servicio por ID, validando pertenencia al negocio."""
    return (
        db.query(Service)
        .filter(Service.id == service_id, Service.business_id == business_id)
        .first()
    )


def create_service(db: Session, data: dict) -> Service:
    """Crea un nuevo servicio y lo persiste."""
    service = Service(**data)
    db.add(service)
    db.commit()
    db.refresh(service)
    logger.info("Servicio creado: id=%s name=%s", service.id, service.name)
    return service


def update_service(db: Session, service_id: int, business_id: int, data: dict) -> Optional[Service]:
    """Actualiza un servicio existente. Retorna None si no existe."""
    service = get_service(db, service_id, business_id)
    if not service:
        return None
    filtered = {k: v for k, v in data.items() if k in SERVICE_ALLOWED_FIELDS}
    for key, value in filtered.items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    logger.info("Servicio actualizado: id=%s", service.id)
    return service


def delete_service(db: Session, service_id: int, business_id: int) -> bool:
    """Soft-delete: desactiva el servicio (is_active=False)."""
    service = get_service(db, service_id, business_id)
    if not service:
        return False
    service.is_active = False
    db.commit()
    logger.info("Servicio desactivado: id=%s", service.id)
    return True


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

def get_products(db: Session, business_id: int) -> list[Product]:
    """Lista todos los productos activos de un negocio."""
    return (
        db.query(Product)
        .filter(Product.business_id == business_id, Product.is_active.is_(True))
        .order_by(Product.name)
        .all()
    )


def get_product(db: Session, product_id: int, business_id: int) -> Optional[Product]:
    """Obtiene un producto por ID, validando pertenencia al negocio."""
    return (
        db.query(Product)
        .filter(Product.id == product_id, Product.business_id == business_id)
        .first()
    )


def create_product(db: Session, data: dict) -> Product:
    """Crea un nuevo producto y lo persiste."""
    product = Product(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info("Producto creado: id=%s name=%s", product.id, product.name)
    return product


def update_product(db: Session, product_id: int, business_id: int, data: dict) -> Optional[Product]:
    """Actualiza un producto existente. Retorna None si no existe."""
    product = get_product(db, product_id, business_id)
    if not product:
        return None
    filtered = {k: v for k, v in data.items() if k in PRODUCT_ALLOWED_FIELDS}
    for key, value in filtered.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    logger.info("Producto actualizado: id=%s", product.id)
    return product


def delete_product(db: Session, product_id: int, business_id: int) -> bool:
    """Soft-delete: desactiva el producto (is_active=False)."""
    product = get_product(db, product_id, business_id)
    if not product:
        return False
    product.is_active = False
    db.commit()
    logger.info("Producto desactivado: id=%s", product.id)
    return True
