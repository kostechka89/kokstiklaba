from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserPublic


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    news_id: UUID


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentRead(CommentBase):
    id: UUID
    news_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommentWithAuthor(CommentRead):
    author: UserPublic
