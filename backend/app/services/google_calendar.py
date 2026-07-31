import json
import logging
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.settings import settings

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Inicializa y retorna el cliente de la API de Google Calendar."""
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON no está configurado en el entorno.")
        return None
    try:
        creds_dict = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error inicializando Google Calendar API: {e}")
        return None

def create_event(calendar_id: str, summary: str, description: str, start_time: datetime, end_time: datetime) -> str | None:
    """Crea un evento en el calendario y retorna su ID."""
    service = get_calendar_service()
    if not service or not calendar_id:
        return None
    
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time.isoformat()},
        'end': {'dateTime': end_time.isoformat()},
    }
    
    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logger.info(f"Evento creado en Google Calendar: {created_event.get('id')}")
        return created_event.get('id')
    except Exception as e:
        logger.error(f"Error creando evento en Google Calendar: {e}")
        return None

def delete_event(calendar_id: str, event_id: str):
    """Elimina un evento del calendario."""
    service = get_calendar_service()
    if not service or not calendar_id or not event_id:
        return
    
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        logger.info(f"Evento eliminado en Google Calendar: {event_id}")
    except Exception as e:
        logger.error(f"Error eliminando evento en Google Calendar: {e}")

def get_freebusy(calendar_id: str, time_min: datetime, time_max: datetime) -> list[tuple[datetime, datetime]]:
    """Consulta los bloques ocupados (busy) en un rango de tiempo."""
    service = get_calendar_service()
    if not service or not calendar_id:
        return []
    
    body = {
        "timeMin": time_min.isoformat(),
        "timeMax": time_max.isoformat(),
        "items": [{"id": calendar_id}]
    }
    
    try:
        eventsResult = service.freebusy().query(body=body).execute()
        busy_slots = eventsResult['calendars'].get(calendar_id, {}).get('busy', [])
        
        # Convertir strings ISO a objetos datetime timezone-aware
        return [
            (datetime.fromisoformat(b['start']), datetime.fromisoformat(b['end']))
            for b in busy_slots
        ]
    except Exception as e:
        logger.error(f"Error consultando disponibilidad en Google Calendar: {e}")
        return []

def get_busy_slots(calendar_id: str, time_min: datetime, time_max: datetime):
    """Alias de compatibilidad para get_freebusy."""
    return get_freebusy(calendar_id, time_min, time_max)