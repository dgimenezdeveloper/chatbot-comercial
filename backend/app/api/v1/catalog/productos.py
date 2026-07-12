from fastapi import APIRouter, status
from typing import List
from app.schemas.catalog import ProductoRequest, ProductoResponse

router = APIRouter()

@router.get("/", response_model=List[ProductoResponse], status_code=status.HTTP_200_OK)
async def listar_productos():
    return [
        ProductoResponse(id=1, nombre="Cera para cabello", precio=2500.0, stock=15, activo=True),
        ProductoResponse(id=2, nombre="Aceite para barba", precio=3200.0, stock=8, activo=True)
    ]

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: ProductoRequest):
    return ProductoResponse(id=3, **payload.model_dump())

@router.put("/{producto_id}", response_model=ProductoResponse, status_code=status.HTTP_200_OK)
async def actualizar_producto(producto_id: int, payload: ProductoRequest):
    return ProductoResponse(id=producto_id, **payload.model_dump())

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int):
    return None