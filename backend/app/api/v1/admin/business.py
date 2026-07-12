"""Endpoint CRUD de negocio — gestión de configuración multi-tenant.

GET  /api/v1/admin/business/{id} — obtener configuración
PUT  /api/v1/admin/business/{id} — actualizar configuración (incl. recordatorios)
"""

from fastapi import APIRouter, Body

from app.db.database import SessionLocal
from app.db.models.business import Business

router = APIRouter()


@router.get("/{business_id}")
async def get_business(business_id: int):
    """Retorna la configuración del negocio."""
    db = SessionLocal()
    try:
        biz = db.query(Business).filter(Business.id == business_id).first()
        if not biz:
            return {"error": "not_found", "business_id": business_id}
        return {
            "id": biz.id,
            "name": biz.name,
            "slug": biz.slug,
            "active": biz.active,
            "timezone": biz.timezone,
            "use_whatsapp_templates": biz.use_whatsapp_templates,
            "owner_phone": biz.owner_phone,
        }
    finally:
        db.close()


@router.put("/{business_id}")
async def update_business(
    business_id: int,
    use_whatsapp_templates: bool | None = Body(None),
    owner_phone: str | None = Body(None),
):
    """Actualiza configuración de recordatorios del negocio."""
    db = SessionLocal()
    try:
        biz = db.query(Business).filter(Business.id == business_id).first()
        if not biz:
            return {"error": "not_found", "business_id": business_id}

        if use_whatsapp_templates is not None:
            biz.use_whatsapp_templates = use_whatsapp_templates
        if owner_phone is not None:
            biz.owner_phone = owner_phone

        db.commit()
        db.refresh(biz)
        return {
            "id": biz.id,
            "name": biz.name,
            "use_whatsapp_templates": biz.use_whatsapp_templates,
            "owner_phone": biz.owner_phone,
        }
    finally:
        db.close()
