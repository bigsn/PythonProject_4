"""Celery app factory and task imports."""

from celery import Celery
from pythonproject_4.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ainews",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    # Sequential Telegram access: one task at a time for telegram-related tasks
    worker_prefetch_multiplier=1,
    # Расписание задач Celery Beat
    beat_schedule={
        # Сбор новостей каждые 30 минут
        "collect-news-every-30-minutes": {
            "task": "pythonproject_4.tasks.collect_all_enabled_sources",
            "schedule": 1800.0,  # 30 минут в секундах
        },
        # Публикация постов в HH:00 и HH:30
        "publish-at-top-of-hour": {
            "task": "pythonproject_4.tasks.schedule_publication",
            "schedule": 1800.0,  # каждые 30 минут
        },
    },
)

# Import tasks to register them
import pythonproject_4.tasks  # noqa: F401


if __name__ == "__main__":
    from celery.bin import celery
    celery.main()
