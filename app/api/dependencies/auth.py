from datetime import datetime
from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.news import News
from app.models.user import User
from app.services.cache import cache_user, get_cached_user
from app.services.security import decode_token
from app.utils.context import CurrentUser

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


async def resolve_user(user_id: str, db: AsyncSession) -> Optional[CurrentUser]:
    cached = await get_cached_user(user_id)
    if cached:
        logger.info("user cache hit for %s", user_id)
        return CurrentUser(
            id=UUID(user_id),
            name=cached["name"],
            email=cached["email"],
            avatar_url=cached.get("avatar_url"),
            is_author=cached["is_author"],
            is_admin=cached["is_admin"],
            registered_at=datetime.fromisoformat(cached["registered_at"]),
        )

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if user:
        await cache_user(
            user_id,
            {
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "is_author": user.is_author,
                "is_admin": user.is_admin,
                "registered_at": user.registered_at.isoformat(),
            },
        )
        return CurrentUser(
            id=user.id,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            is_author=user.is_author,
            is_admin=user.is_admin,
            registered_at=user.registered_at,
        )
    return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await resolve_user(payload["sub"], db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def role_required(*, allow_admin: bool = True, author: bool = False) -> Callable[[CurrentUser], CurrentUser]:
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if allow_admin and user.is_admin:
            return user
        if author and user.is_author:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return dependency


async def load_news(
    news_id: str,
    db: AsyncSession = Depends(get_db),
) -> News:
    result = await db.execute(select(News).where(News.id == UUID(news_id)))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return news


def news_owner_or_admin() -> Callable[[News, CurrentUser], News]:
    async def dependency(
        news: News = Depends(load_news),
        user: CurrentUser = Depends(get_current_user),
    ) -> News:
        if user.is_admin or news.author_id == user.id:
            return news
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return dependency


async def load_comment_owner(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
):
    from app.models.comment import Comment

    result = await db.execute(select(Comment).where(Comment.id == UUID(comment_id)))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


def comment_owner_or_admin():
    async def dependency(
        comment = Depends(load_comment_owner),
        user: CurrentUser = Depends(get_current_user),
    ):
        if user.is_admin or comment.author_id == user.id:
            return comment
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return dependency
