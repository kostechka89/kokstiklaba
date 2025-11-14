from datetime import datetime, timedelta
from typing import Tuple

from app.core.config import get_settings
from app.models.user import User
from app.schemas.auth import TokenPair
from app.services.cache import cache_session
from app.services.security import create_token, generate_session_id

settings = get_settings()


async def create_token_pair(user: User, user_agent: str) -> Tuple[TokenPair, str]:
    session_id = generate_session_id()
    access_token = create_token(
        str(user.id),
        session_id,
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_token(
        str(user.id),
        session_id,
        timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=settings.refresh_token_expire_minutes)
    await cache_session(
        session_id,
        {"user_id": str(user.id), "user_agent": user_agent, "created_at": created_at, "expires_at": expires_at},
        settings.refresh_token_expire_minutes * 60,
    )
    token_pair = TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_minutes * 60,
    )
    return token_pair, session_id
