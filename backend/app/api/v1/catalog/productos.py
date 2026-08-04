"""Router de productos de catálogo — conectado a PostgreSQL con CRUD completo."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.catalog import ProductoRequest, ProductoResponse, PedidoResponse, PedidoEstadoRequest
from app.db.models.product_order import ProductOrder
from app.services.catalog import (
    create_product,
    delete_product,
    get_products,
    update_product,
)

router = APIRouter()


@router.get("/", response_model=List[ProductoResponse], status_code=status.HTTP_200_OK)
async def listar_productos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    products_db = get_products(db, business_id=business_id, include_inactive=True)
    
    return [
        ProductoResponse(
            id=p.id,
            nombre=p.name,
            descripcion=p.description or "",
            precio=float(p.price or 0.0),
            stock=p.stock_quantity or 0,
            activo=p.is_active if p.is_active is not None else True
        )
        for p in products_db
    ]


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto_endpoint(
    payload: ProductoRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)

    raw_slug = payload.nombre.lower().replace(" ", "-").replace("/", "-")
    clean_slug = "".join(c for c in raw_slug if c.isalnum() or c == "-")
    unique_slug = f"{clean_slug[:60]}-{business_id}-{uuid.uuid4().hex[:6]}"

    data = {
        "business_id": business_id,
        "name": payload.nombre,
        "slug": unique_slug,
        "description": payload.descripcion,
        "price": payload.precio,
        "stock_quantity": payload.stock,
        "is_active": payload.activo if payload.activo is not None else True,
    }

    new_prod = create_product(db, data)
    return ProductoResponse(
        id=new_prod.id,
        nombre=new_prod.name,
        descripcion=new_prod.description or "",
        precio=float(new_prod.price or 0.0),
        stock=new_prod.stock_quantity or 0,
        activo=new_prod.is_active if new_prod.is_active is not None else True
    )

@router.get("/pedidos", response_model=List[PedidoResponse], status_code=status.HTTP_200_OK)
async def listar_pedidos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    pedidos = db.query(ProductOrder).filter(ProductOrder.business_id == business_id).order_by(ProductOrder.created_at.desc()).all()
    return pedidos

@router.put("/pedidos/{pedido_id}/estado", response_model=PedidoResponse, status_code=status.HTTP_200_OK)
async def actualizar_estado_pedido(
    pedido_id: int,
    payload: PedidoEstadoRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    pedido = db.query(ProductOrder).filter(ProductOrder.id == pedido_id, ProductOrder.business_id == business_id).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    pedido.status = payload.estado
    db.commit()
    db.refresh(pedido)
    return pedido

@router.put("/{producto_id}", response_model=ProductoResponse, status_code=status.HTTP_200_OK)
async def actualizar_producto_endpoint(
    producto_id: int,
    payload: ProductoRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)

    data = {
        "name": payload.nombre,
        "description": payload.descripcion,
        "price": payload.precio,
        "stock_quantity": payload.stock,
        "is_active": payload.activo if payload.activo is not None else True,
    }

    updated = update_product(db, product_id=producto_id, business_id=business_id, data=data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado o no pertenece a este comercio."
        )

    return ProductoResponse(
        id=updated.id,
        nombre=updated.name,
        descripcion=updated.description or "",
        precio=float(updated.price or 0.0),
        stock=updated.stock_quantity or 0,
        activo=updated.is_active if updated.is_active is not None else True
    )


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto_endpoint(
    producto_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    business_id = current_user.get("business_id", 1)
    success = delete_product(db, product_id=producto_id, business_id=business_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado o no pertenece a este comercio."
        )
    return None