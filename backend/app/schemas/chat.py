from pydantic import BaseModel, Field

class MensajeRequest(BaseModel):
    telefono: str = Field(..., description="Número de WhatsApp del cliente en formato string")
    mensaje: str = Field(..., description="Contenido del mensaje enviado por el usuario")

class MensajeResponse(BaseModel):
    respuesta: str = Field(..., description="Texto de respuesta generado por el bot")
    tipo: str = Field(default="text", description="Tipo de mensaje, por defecto 'text'")