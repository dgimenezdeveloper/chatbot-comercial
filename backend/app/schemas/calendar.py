from pydantic import BaseModel, ConfigDict, Field

class TurnoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telefono: str = Field(..., description="Número de teléfono del cliente")
    servicio_id: int = Field(..., description="ID del servicio a reservar")
    fecha: str = Field(..., description="Fecha del turno en formato YYYY-MM-DD")
    hora: str = Field(..., description="Hora del turno en formato HH:MM")

class TurnoResponse(TurnoRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único del turno")
    estado: str = Field(default="confirmado", description="Estado actual del turno (ej. confirmado, cancelado)")