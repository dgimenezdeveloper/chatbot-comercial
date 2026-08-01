"""Router de servicios de catálogo — conectado a PostgreSQL con CRUD completo."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.catalog import ServicioRequest, ServicioResponse
from app.services.catalog import (
    create_service,
    delete_service,
    get_services,
    update_service,
)

router = APIRouter()


@router.get("/", response_model=List[ServicioResponse], status_code=status.HTTP_200_OK)
async def listar_servicios(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna los servicios activos de PostgreSQL para el negocio autenticado."""
    business_id = current_user.get("business_id", 1)
    services_db = get_services(db, business_id=business_id)
    
    return [
        ServicioResponse(
            id=s.id,
            nombre=s.name,
            descripcion=s.description or "",
            duracion_minutos=s.duration_minutes or 30,
            precio=float(s.price or 0.0)
        )
        for s in services_db
    ]


@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def crear_servicio(
    payload: ServicioRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un nuevo servicio para el negocio autenticado."""
    business_id = current_user.get("business_id", 1)
    
    # Generar un slug único por comercio evitando colisiones
    raw_slug = payload.nombre.lower().replace(" ", "-").replace("/", "-")
    clean_slug = "".join(c for c in raw_slug if c.isalnum() or c == "-")
    unique_slug = f"{clean_slug[:60]}-{business_id}-{uuid.uuid4().hex[:6]}"

    data = {
        "business_id": business_id,
        "name": payload.nombre,
        "slug": unique_slug,
        "description": payload.descripcion,
        "category": "otros",
        "price": payload.precio,
        "duration_minutes": payload.duracion_minutos,
        "is_active": True,
    }

    new_svc = create_service(db, data)
    return ServicioResponse(
        id=new_svc.id,
        nombre=new_svc.name,
        descripcion=new_svc.description or "",
        duracion_minutos=new_svc.duration_minutes or 30,
        precio=float(new_svc.price or 0.0)
    )


@router.put("/{servicio_id}", response_model=ServicioResponse, status_code=status.HTTP_200_OK)
async def actualizar_servicio_endpoint(
    servicio_id: int,
    payload: ServicioRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza un servicio existente."""
    business_id = current_user.get("business_id", 1)

    data = {
        "name": payload.nombre,
        "description": payload.descripcion,
        "price": payload.precio,
        "duration_minutes": payload.duracion_minutos,
    }

    updated = update_service(db, service_id=servicio_id, business_id=business_id, data=data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado o no pertenece a este comercio."
        )

    return ServicioResponse(
        id=updated.id,
        nombre=updated.name,
        descripcion=updated.description or "",
        duracion_minutos=updated.duration_minutes or 30,
        precio=float(updated.price or 0.0)
    )


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_servicio_endpoint(
    servicio_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina (desactiva) un servicio por ID."""
    business_id = current_user.get("business_id", 1)
    success = delete_service(db, service_id=servicio_id, business_id=business_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado o no pertenece a este comercio."
        )
    return None