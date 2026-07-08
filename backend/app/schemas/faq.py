from pydantic import BaseModel, Field

class FAQRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta frecuente realizada por los clientes")
    respuesta: str = Field(..., description="Respuesta a la pregunta frecuente")

class FAQResponse(FAQRequest):
    id: int = Field(..., description="Identificador único de la FAQ")