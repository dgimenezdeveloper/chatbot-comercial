from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime

class ServicioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., min_length=3, description="Nombre del servicio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del servicio")
    duracion_minutos: int = Field(..., description="Duración estimada en minutos")
    precio: float = Field(..., gt=0, description="Precio del servicio")
    activo: Optional[bool] = Field(True, description="Indica si el servicio está activo")

    @field_validator('nombre')
    @classmethod
    def validate_nombre_alfanumerico(cls, v: str) -> str:
        # Validar que contenga al menos 3 caracteres alfanuméricos
        alnum_count = sum(c.isalnum() for c in v)
        if alnum_count < 3:
            raise ValueError("El nombre debe contener al menos 3 caracteres alfanuméricos")
        return v

class ServicioResponse(ServicioRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del servicio")
    activo: bool = Field(True, description="Indica si el servicio está activo")

class ProductoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., min_length=3, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del producto")
    precio: float = Field(..., gt=0, description="Precio de venta")
    stock: int = Field(..., description="Cantidad disponible en inventario")
    activo: bool = Field(True, description="Indica si el producto está activo para la venta")

    @field_validator('nombre')
    @classmethod
    def validate_nombre_alfanumerico(cls, v: str) -> str:
        alnum_count = sum(c.isalnum() for c in v)
        if alnum_count < 3:
            raise ValueError("El nombre debe contener al menos 3 caracteres alfanuméricos")
        return v

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