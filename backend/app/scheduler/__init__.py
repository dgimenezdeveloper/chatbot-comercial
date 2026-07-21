"""Scheduler module — Celery tasks para recordatorios automáticos."""

from app.scheduler.config import celery_app

__all__ = ["celery_app"]
