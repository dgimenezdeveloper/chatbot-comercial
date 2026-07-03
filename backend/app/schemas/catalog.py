from pydantic import BaseModel, Field
from typing import Optional

class ServicioRequest(BaseModel):
    nombre: str = Field(..., description="Nombre del servicio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del servicio")
    duracion_minutos: int = Field(..., description="Duración estimada en minutos")
    precio: float = Field(..., description="Precio del servicio")

class ServicioResponse(ServicioRequest):
    id: int = Field(..., description="Identificador único del servicio")

class ProductoRequest(BaseModel):
    nombre: str = Field(..., description="Nombre del producto")
    precio: float = Field(..., description="Precio de venta")
    stock: int = Field(..., description="Cantidad disponible en inventario")
    activo: bool = Field(True, description="Indica si el producto está activo para la venta")

class ProductoResponse(ProductoRequest):
    id: int = Field(..., description="Identificador único del producto")