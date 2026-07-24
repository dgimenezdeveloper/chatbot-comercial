"""Endpoint CRUD de negocio — gestión de configuración multi-tenant.

GET  /api/v1/admin/business/{id} — obtener configuración
PUT  /api/v1/admin/business/{id} — actualizar configuración
"""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.business import Business

router = APIRouter()


@router.get("/{business_id}")
async def get_business(
    business_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna la configuración del negocio validando que coincida con el JWT."""
    user_business_id = current_user.get("business_id", 1)
    if business_id != user_business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: No tienes permisos para acceder a otro comercio."
        )

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


@router.put("/{business_id}")
async def update_business(
    business_id: int,
    use_whatsapp_templates: bool | None = Body(None),
    owner_phone: str | None = Body(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza configuración de recordatorios del negocio de la sesión."""
    user_business_id = current_user.get("business_id", 1)
    if business_id != user_business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: No tienes permisos para modificar otro comercio."
        )

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