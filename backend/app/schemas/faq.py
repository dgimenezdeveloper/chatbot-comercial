from pydantic import BaseModel, ConfigDict, Field

class FAQRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pregunta: str = Field(..., description="Pregunta frecuente realizada por los clientes")
    respuesta: str = Field(..., description="Respuesta a la pregunta frecuente")

class FAQResponse(FAQRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador único de la FAQ")