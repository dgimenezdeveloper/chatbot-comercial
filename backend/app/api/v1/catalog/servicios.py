"""Router de servicios de catálogo — conectado a PostgreSQL."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.catalog import ServicioRequest, ServicioResponse
from app.services.catalog import get_services

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