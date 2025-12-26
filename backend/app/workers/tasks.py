from celery import Celery
import logging
from datetime import datetime
from app.core.config import get_settings
from app.services.metrics import NOTIFICATIONS_SENT

settings = get_settings()
celery_app = Celery("worker", broker=settings.redis_url, backend=settings.redis_url)

logger = logging.getLogger("notifications")
handler = logging.FileHandler("notifications.log")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_news_notification(self, user_email: str, news_id: int):
    message = f"{datetime.utcnow().isoformat()} send news {news_id} to {user_email}"
    logger.info(message)
    NOTIFICATIONS_SENT.inc()
    return message


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_weekly_digest(self, user_email: str, news_ids: list[int]):
    message = f"{datetime.utcnow().isoformat()} digest {news_ids} to {user_email}"
    logger.info(message)
    NOTIFICATIONS_SENT.inc(len(news_ids))
    return message
