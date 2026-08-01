"""Router de configuración de negocio y gestión de clientes."""

import zoneinfo
from datetime import timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.appointment import Appointment
from app.db.models.business import Business
from app.schemas.admin import NegocioRequest, NegocioResponse
from app.services.negocio import get_business_timezone

router = APIRouter()


@router.get("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def obtener_negocio(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    biz = db.query(Business).filter(Business.id == business_id).first()
    
    if biz:
        return NegocioResponse(
            id=biz.id,
            nombre=getattr(biz, 'name', f"Comercio ID {business_id}"),
            descripcion=getattr(biz, 'description', "Sin descripción") or "Sin descripción",
            categoria=getattr(biz, 'category', "") or "",
            direccion=getattr(biz, 'address', "") or "",
            telefono=getattr(biz, 'phone', "") or "",
            email=getattr(biz, 'email', "") or "",
            website=getattr(biz, 'website', "") or "",
            instagram=getattr(biz, 'instagram', "") or "",
            facebook=getattr(biz, 'facebook', "") or "",
            tiktok=getattr(biz, 'tiktok', "") or "",
            twitter=getattr(biz, 'twitter', "") or "",
            horarios=getattr(biz, 'horarios', "Lunes a Sábados de 09:00 a 20:00") or "Lunes a Sábados de 09:00 a 20:00",
            contacto=getattr(biz, 'contacto', "Tel: Sin teléfono") or "Sin definir",
            owner_phone=getattr(biz, 'owner_phone', "") or "",
            google_calendar_id=getattr(biz, 'google_calendar_id', "") or "",
            enable_services=getattr(biz, 'enable_services', True),
            enable_products=getattr(biz, 'enable_products', True),
            enable_faqs=getattr(biz, 'enable_faqs', True),
            use_whatsapp_templates=getattr(biz, 'use_whatsapp_templates', False),
            sms_enabled=getattr(biz, 'sms_enabled', False),
            email_enabled=getattr(biz, 'email_enabled', False)
        )
    
    return NegocioResponse(
        id=business_id,
        nombre=f"Comercio ID {business_id}",
        descripcion="Comercio registrado",
        categoria="",
        direccion="",
        telefono="",
        email="",
        website="",
        instagram="",
        facebook="",
        tiktok="",
        twitter="",
        horarios="Sin definir",
        contacto="Sin definir",
        owner_phone="",
        google_calendar_id="",
        enable_services=True,
        enable_products=True,
        enable_faqs=True,
        use_whatsapp_templates=False,
        sms_enabled=False,
        email_enabled=False
    )


@router.put("/", response_model=NegocioResponse, status_code=status.HTTP_200_OK)
async def actualizar_negocio(
    payload: NegocioRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    biz = db.query(Business).filter(Business.id == business_id).first()
    if biz:
        biz.name = payload.nombre
        biz.description = payload.descripcion
        
        if hasattr(biz, 'category') and payload.categoria is not None: biz.category = payload.categoria
        if hasattr(biz, 'address') and payload.direccion is not None: biz.address = payload.direccion
        if hasattr(biz, 'phone') and payload.telefono is not None: biz.phone = payload.telefono
        if hasattr(biz, 'email') and payload.email is not None: biz.email = payload.email
        if hasattr(biz, 'website') and payload.website is not None: biz.website = payload.website
        if hasattr(biz, 'instagram') and payload.instagram is not None: biz.instagram = payload.instagram
        if hasattr(biz, 'facebook') and payload.facebook is not None: biz.facebook = payload.facebook
        if hasattr(biz, 'tiktok') and payload.tiktok is not None: biz.tiktok = payload.tiktok
        if hasattr(biz, 'twitter') and payload.twitter is not None: biz.twitter = payload.twitter
        if hasattr(biz, 'google_calendar_id') and payload.google_calendar_id is not None: biz.google_calendar_id = payload.google_calendar_id
        
        biz.horarios = payload.horarios
        biz.contacto = payload.contacto
        if payload.owner_phone is not None: biz.owner_phone = payload.owner_phone
            
        if hasattr(biz, 'enable_services'): biz.enable_services = payload.enable_services
        if hasattr(biz, 'enable_products'): biz.enable_products = payload.enable_products
        if hasattr(biz, 'enable_faqs'): biz.enable_faqs = payload.enable_faqs
        
        if hasattr(biz, 'use_whatsapp_templates') and payload.use_whatsapp_templates is not None: biz.use_whatsapp_templates = payload.use_whatsapp_templates
        if hasattr(biz, 'sms_enabled') and payload.sms_enabled is not None: biz.sms_enabled = payload.sms_enabled
        if hasattr(biz, 'email_enabled') and payload.email_enabled is not None: biz.email_enabled = payload.email_enabled
        
        db.commit()
        db.refresh(biz)
        return NegocioResponse(id=biz.id, **payload.model_dump())
        
    return NegocioResponse(id=business_id, **payload.model_dump())


@router.get("/clientes", status_code=status.HTTP_200_OK)
async def listar_clientes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    tz_str = get_business_timezone(db, business_id)
    tz = zoneinfo.ZoneInfo(tz_str)

    appointments = (
        db.query(
            Appointment.user_name,
            Appointment.user_phone,
            func.count(Appointment.id).label("total_turnos"),
            func.max(Appointment.scheduled_date).label("ultimo_turno")
        )
        .filter(Appointment.business_id == business_id)
        .group_by(Appointment.user_name, Appointment.user_phone)
        .all()
    )

    client_list = []
    for idx, appt in enumerate(appointments):
        phone = appt.user_phone or "Sin teléfono"
        last_visit_str = "Sin visitas"
        if appt.ultimo_turno:
            dt = appt.ultimo_turno
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            last_visit_str = dt.astimezone(tz).strftime("%d/%m/%Y")

        client_list.append({
            "id": str(idx + 1),
            "name": appt.user_name or f"Cliente {phone[-4:]}",
            "phone": phone,
            "appointments": appt.total_turnos,
            "lastVisit": last_visit_str
        })

    return client_list