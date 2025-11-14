from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserPublic


class NewsBase(BaseModel):
    title: str
    content: Dict[str, Any]
    cover_url: Optional[str] = None


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    cover_url: Optional[str] = None


class NewsRead(NewsBase):
    id: UUID
    author_id: UUID
    published_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class NewsWithAuthor(NewsRead):
    author: UserPublic
