from celery import Celery
import logging
from datetime import datetime
from app.core.config import get_settings
from datetime import timedelta
from app.services.metrics import NOTIFICATIONS_SENT
from app.services.cache import cache_service
from app.db.session import SessionLocal
from app.db.models import User, News

settings = get_settings()
celery_app = Celery("worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "app.workers.tasks.send_weekly_digest",
        "schedule": 60 * 60 * 24 * 7,
    }
}

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
def send_weekly_digest(self):
    week_key = datetime.utcnow().strftime("%Y-%W")
    start = datetime.utcnow() - timedelta(days=7)
    db = SessionLocal()
    try:
        users = db.query(User).all()
        news_ids = [news.id for news in db.query(News).filter(News.published_at >= start).all()]
    finally:
        db.close()
    for user in users:
        dedupe_key = f"digest:{week_key}:{user.email}"
        if cache_service.get_json(dedupe_key):
            continue
        cache_service.set_json(dedupe_key, True, ttl=60 * 60 * 24 * 7)
        message = f"{datetime.utcnow().isoformat()} digest {news_ids} to {user.email}"
        logger.info(message)
        NOTIFICATIONS_SENT.inc(len(news_ids))
    return {"status": "sent"}
