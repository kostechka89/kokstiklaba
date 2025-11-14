import asyncio
from datetime import datetime
from pathlib import Path
from typing import Iterable

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings
from app.core.logging import logger
from app.services.cache import redis_manager

settings = get_settings()

celery_app = Celery(
    "news_notifications",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "app.services.notifications.send_weekly_digest",
        "schedule": crontab(day_of_week="sun", hour=9, minute=0),
    }
}
celery_app.conf.timezone = "UTC"
celery_app.conf.worker_cancel_long_running_tasks_on_connection_loss = True
celery_app.conf.worker_pool_restarts = True

LOG_FILE = Path("logs/notifications.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _log_delivery(event: str, recipients: Iterable[str], payload: dict) -> None:
    timestamp = datetime.utcnow().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as stream:
        for recipient in recipients:
            line = f"{timestamp}\t{event}\t{recipient}\t{payload}\n"
            stream.write(line)
            logger.info("notification %s to %s payload=%s", event, recipient, payload)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=2, retry_kwargs={"max_retries": 5})
def send_news_created(self, news_id: str, title: str, recipients: Iterable[str]):
    cache_key = f"notification:news:{news_id}"
    was_sent = asyncio.run(redis_manager.client.get(cache_key))
    if was_sent:
        logger.info("skip duplicate notification for news %s", news_id)
        return
    payload = {"news_id": news_id, "title": title, "sent_at": datetime.utcnow().isoformat()}
    _log_delivery("news_created", recipients, payload)
    asyncio.run(redis_manager.client.setex(cache_key, 60 * 60 * 24, "sent"))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=2, retry_kwargs={"max_retries": 5})
def send_weekly_digest(self):
    payload = {"generated_at": datetime.utcnow().isoformat()}
    _log_delivery("weekly_digest", ["all-users"], payload)

