import json
from datetime import datetime
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


class RedisManager:
    def __init__(self) -> None:
        self._client: Optional[Redis] = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client


redis_manager = RedisManager()


async def cache_news(news_id: str, data: Dict[str, Any]) -> None:
    await redis_manager.client.setex(
        f"news:{news_id}", settings.news_cache_ttl_seconds, json.dumps(data, default=str)
    )


async def get_cached_news(news_id: str) -> Optional[Dict[str, Any]]:
    raw = await redis_manager.client.get(f"news:{news_id}")
    if raw:
        return json.loads(raw)
    return None


async def cache_user(user_id: str, data: Dict[str, Any]) -> None:
    await redis_manager.client.setex(
        f"user:{user_id}", settings.refresh_token_expire_minutes * 60, json.dumps(data, default=str)
    )


async def get_cached_user(user_id: str) -> Optional[Dict[str, Any]]:
    raw = await redis_manager.client.get(f"user:{user_id}")
    if raw:
        return json.loads(raw)
    return None


async def cache_session(session_id: str, data: Dict[str, Any], ttl_seconds: int) -> None:
    payload = json.dumps(
        {
            **data,
            "created_at": data["created_at"].isoformat(),
            "expires_at": data["expires_at"].isoformat(),
        }
    )
    await redis_manager.client.setex(f"session:{session_id}", ttl_seconds, payload)


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    raw = await redis_manager.client.get(f"session:{session_id}")
    if not raw:
        return None
    payload = json.loads(raw)
    payload["created_at"] = datetime.fromisoformat(payload["created_at"])
    payload["expires_at"] = datetime.fromisoformat(payload["expires_at"])
    return payload


async def delete_session(session_id: str) -> None:
    await redis_manager.client.delete(f"session:{session_id}")


async def list_sessions(user_id: str) -> Dict[str, Dict[str, Any]]:
    cursor = 0
    sessions: Dict[str, Dict[str, Any]] = {}
    while True:
        cursor, keys = await redis_manager.client.scan(cursor=cursor, match="session:*", count=100)
        for key in keys:
            raw = await redis_manager.client.get(key)
            if not raw:
                continue
            payload = json.loads(raw)
            if payload.get("user_id") == user_id:
                payload["created_at"] = datetime.fromisoformat(payload["created_at"])
                payload["expires_at"] = datetime.fromisoformat(payload["expires_at"])
                sessions[key.replace("session:", "")] = payload
        if cursor == 0:
            break
    return sessions
