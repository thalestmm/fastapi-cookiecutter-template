"""
Celery worker configuration and application instance.
"""
import logging
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from celery.schedules import crontab
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app instance
celery_app = Celery(
    "{{ cookiecutter.project_slug }}",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery Configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)

# Celery Beat Configuration
celery_app.conf.beat_schedule = {
    # TODO: Replace with the desired tasks
    'run-task-every-minute': {
        'task': 'app.worker.tasks.long_running_task',
        'schedule': 60.0,
    },
    'run-task-on-schedule': {
        'task': 'app.worker.tasks.long_running_task',
        'schedule': crontab(hour=12, minute=0),
    },
}

# Auto-discover tasks in the tasks module
celery_app.autodiscover_tasks(['app.worker'], related_name='tasks')


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """Called when worker is ready to accept tasks."""
    logger.info("=" * 80)
    logger.info("Celery worker is ready")
    logger.info(f"Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"Backend: {settings.CELERY_RESULT_BACKEND}")
    logger.info("=" * 80)


@worker_shutdown.connect
def on_worker_shutdown(sender, **kwargs):
    """Called when worker is shutting down."""
    logger.info("Celery worker shutting down...")


# Export for easier imports
app = celery_app

__all__ = ["celery_app", "app"]