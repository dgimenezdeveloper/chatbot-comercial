from fastapi import APIRouter, status
from app.schemas.chat import MensajeRequest, MensajeResponse

router = APIRouter()

@router.post("/chat", response_model=MensajeResponse, status_code=status.HTTP_200_OK)
async def chat(payload: MensajeRequest):
    """
    Endpoint para procesar los mensajes del cliente final (Mock inicial).
    """
    respuesta_mock = f"¡Hola! Recibí tu mensaje: '{payload.mensaje}'. ¿En qué puedo ayudarte con tu turno?"
    return MensajeResponse(respuesta=respuesta_mock, tipo="text")