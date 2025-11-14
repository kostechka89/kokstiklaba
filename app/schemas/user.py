from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    is_author: bool = False
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_author: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserRead(UserBase):
    id: UUID
    registered_at: datetime

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    is_author: bool
    is_admin: bool
    registered_at: datetime

    class Config:
        orm_mode = True
