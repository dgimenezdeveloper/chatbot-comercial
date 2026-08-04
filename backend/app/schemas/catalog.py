from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class ServicioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre del servicio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del servicio")
    duracion_minutos: int = Field(..., description="Duración estimada en minutos")
    precio: float = Field(..., description="Precio del servicio")
    activo: Optional[bool] = Field(True, description="Indica si el servicio está activo")

class ServicioResponse(ServicioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del servicio")
    activo: bool = Field(True, description="Indica si el servicio está activo")

class ProductoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del producto")
    precio: float = Field(..., description="Precio de venta")
    stock: int = Field(..., description="Cantidad disponible en inventario")
    activo: bool = Field(True, description="Indica si el producto está activo para la venta")

class ProductoResponse(ProductoRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del producto")

class PedidoEstadoRequest(BaseModel):
    estado: str = Field(..., description="Nuevo estado: pendiente, entregado, cancelado")

class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_name: Optional[str]
    user_phone: Optional[str]
    items_json: list
    total_price: float
    status: str
    created_at: datetime