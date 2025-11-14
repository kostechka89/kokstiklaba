from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, news_owner_or_admin, role_required
from app.core.logging import logger
from app.db.session import get_db
from app.models.news import News
from app.models.user import User
from app.schemas.news import NewsCreate, NewsRead, NewsUpdate, NewsWithAuthor
from app.schemas.user import UserPublic
from app.services.cache import cache_news, get_cached_news, redis_manager
from app.services.notifications import send_news_created
from app.utils.context import CurrentUser

router = APIRouter(prefix="/news", tags=["news"])


@router.post(
    "/",
    response_model=NewsRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required(author=True))],
)
async def create_news(
    payload: NewsCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NewsRead:
    news = News(
        title=payload.title,
        content=payload.content,
        cover_url=payload.cover_url,
        author_id=current_user.id,
        published_at=datetime.utcnow(),
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)

    await cache_news(
        str(news.id),
        {
            "id": str(news.id),
            "title": news.title,
            "content": news.content,
            "cover_url": news.cover_url,
            "author_id": str(news.author_id),
            "published_at": news.published_at.isoformat(),
            "updated_at": news.updated_at.isoformat(),
        },
    )

    result = await db.execute(select(User.email))
    recipients = [email for email in result.scalars().all() if email]
    try:
        send_news_created.delay(str(news.id), news.title, recipients)
    except Exception as exc:
        logger.warning("failed to enqueue news notification: %s", exc)

    return NewsRead.from_orm(news)


@router.get("/", response_model=list[NewsRead])
async def list_news(db: AsyncSession = Depends(get_db)) -> list[NewsRead]:
    result = await db.execute(select(News))
    news_list = result.scalars().all()
    response = []
    for news in news_list:
        await cache_news(
            str(news.id),
            {
                "id": str(news.id),
                "title": news.title,
                "content": news.content,
                "cover_url": news.cover_url,
                "author_id": str(news.author_id),
                "published_at": news.published_at.isoformat(),
                "updated_at": news.updated_at.isoformat(),
            },
        )
        response.append(NewsRead.from_orm(news))
    return response


@router.get("/{news_id}", response_model=NewsWithAuthor)
async def get_news(news_id: UUID, db: AsyncSession = Depends(get_db)) -> NewsWithAuthor:
    cached = await get_cached_news(str(news_id))
    if cached:
        logger.info("news %s served from cache", news_id)
        author_result = await db.execute(select(User).where(User.id == UUID(cached["author_id"])))
        author = author_result.scalar_one()
        return NewsWithAuthor(
            id=news_id,
            title=cached["title"],
            content=cached["content"],
            cover_url=cached.get("cover_url"),
            author_id=UUID(cached["author_id"]),
            published_at=datetime.fromisoformat(cached["published_at"]),
            updated_at=datetime.fromisoformat(cached["updated_at"]),
            author=UserPublic.from_orm(author),
        )

    logger.info("news %s loaded from database", news_id)
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    await cache_news(
        str(news.id),
        {
            "id": str(news.id),
            "title": news.title,
            "content": news.content,
            "cover_url": news.cover_url,
            "author_id": str(news.author_id),
            "published_at": news.published_at.isoformat(),
            "updated_at": news.updated_at.isoformat(),
        },
    )
    await db.refresh(news, attribute_names=["author"])
    return NewsWithAuthor.from_orm(news)


@router.put("/{news_id}", response_model=NewsRead)
async def update_news(
    payload: NewsUpdate,
    news: News = Depends(news_owner_or_admin()),
    db: AsyncSession = Depends(get_db),
) -> NewsRead:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(news, field, value)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    await cache_news(
        str(news.id),
        {
            "id": str(news.id),
            "title": news.title,
            "content": news.content,
            "cover_url": news.cover_url,
            "author_id": str(news.author_id),
            "published_at": news.published_at.isoformat(),
            "updated_at": news.updated_at.isoformat(),
        },
    )
    return NewsRead.from_orm(news)


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(news: News = Depends(news_owner_or_admin()), db: AsyncSession = Depends(get_db)) -> None:
    await db.delete(news)
    await db.commit()
    await redis_manager.client.delete(f"news:{news.id}")
