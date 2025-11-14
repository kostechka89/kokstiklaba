from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import comment_owner_or_admin, get_current_user
from app.db.session import get_db
from app.models.comment import Comment
from app.models.news import News
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate, CommentWithAuthor
from app.utils.context import CurrentUser

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentRead:
    result = await db.execute(select(News).where(News.id == payload.news_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    comment = Comment(
        text=payload.text,
        news_id=payload.news_id,
        author_id=current_user.id,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentRead.from_orm(comment)


@router.get("/{comment_id}", response_model=CommentWithAuthor)
async def get_comment(comment_id: UUID, db: AsyncSession = Depends(get_db)) -> CommentWithAuthor:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.refresh(comment, attribute_names=["author"])
    return CommentWithAuthor.from_orm(comment)


@router.get("/news/{news_id}", response_model=list[CommentWithAuthor])
async def list_comments(news_id: UUID, db: AsyncSession = Depends(get_db)) -> list[CommentWithAuthor]:
    result = await db.execute(select(Comment).where(Comment.news_id == news_id))
    comments = result.scalars().all()
    response = []
    for comment in comments:
        await db.refresh(comment, attribute_names=["author"])
        response.append(CommentWithAuthor.from_orm(comment))
    return response


@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(
    payload: CommentUpdate,
    comment: Comment = Depends(comment_owner_or_admin()),
    db: AsyncSession = Depends(get_db),
) -> CommentRead:
    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(comment, field, value)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentRead.from_orm(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment: Comment = Depends(comment_owner_or_admin()), db: AsyncSession = Depends(get_db)) -> None:
    await db.delete(comment)
    await db.commit()
