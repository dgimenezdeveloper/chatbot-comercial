"""Celery app instance — shared between worker and tasks."""

from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "chatbot_comercial",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Argentina/Buenos_Aires",
    enable_utc=True,
    beat_schedule={
        "send-reminders-daily-9am": {
            "task": "app.scheduler.tasks.send_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
    },
)
