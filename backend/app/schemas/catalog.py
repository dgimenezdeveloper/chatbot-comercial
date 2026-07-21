from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ServicioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre del servicio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del servicio")
    duracion_minutos: int = Field(..., description="Duración estimada en minutos")
    precio: float = Field(..., description="Precio del servicio")

class ServicioResponse(ServicioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del servicio")

class ProductoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre del producto")
    precio: float = Field(..., description="Precio de venta")
    stock: int = Field(..., description="Cantidad disponible en inventario")
    activo: bool = Field(True, description="Indica si el producto está activo para la venta")

class ProductoResponse(ProductoRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del producto")