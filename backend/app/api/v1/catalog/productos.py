"""Router de productos de catálogo — conectado a PostgreSQL."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.catalog import ProductoRequest, ProductoResponse
from app.services.catalog import get_products

router = APIRouter()


@router.get("/", response_model=List[ProductoResponse], status_code=status.HTTP_200_OK)
async def listar_productos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna los productos activos de PostgreSQL para el negocio autenticado."""
    business_id = current_user.get("business_id", 1)
    products_db = get_products(db, business_id=business_id)
    
    return [
        ProductoResponse(
            id=p.id,
            nombre=p.name,
            precio=float(p.price or 0.0),
            stock=p.stock_quantity or 0,
            activo=p.is_active if p.is_active is not None else True
        )
        for p in products_db
    ]