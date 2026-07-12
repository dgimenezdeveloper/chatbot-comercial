from pydantic import BaseModel, Field

class TurnoRequest(BaseModel):
    telefono: str = Field(..., description="Número de teléfono del cliente")
    servicio_id: int = Field(..., description="ID del servicio a reservar")
    fecha: str = Field(..., description="Fecha del turno en formato YYYY-MM-DD")
    hora: str = Field(..., description="Hora del turno en formato HH:MM")

class TurnoResponse(TurnoRequest):
    id: int = Field(..., description="Identificador único del turno")
    estado: str = Field(default="confirmado", description="Estado actual del turno (ej. confirmado, cancelado)")