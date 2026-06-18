from fastapi import APIRouter, Query, Response, status

router = APIRouter()

@router.get("/webhook")
async def verificar_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificación exigido por Meta WABA.
    """
    if mode == "subscribe" and token:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verificación fallida", status_code=status.HTTP_403_FORBIDDEN)

@router.post("/webhook")
async def recibir_mensaje_waba(payload: dict):
    """
    Endpoint de recepción de eventos JSON desde WhatsApp de Meta.
    """
    return Response(content="EVENT_RECEIVED", status_code=status.HTTP_200_OK)