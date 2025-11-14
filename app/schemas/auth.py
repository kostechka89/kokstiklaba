from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class TokenPayload(BaseModel):
    sub: str
    session_id: str
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class SessionInfo(BaseModel):
    session_id: str
    user_agent: Optional[str]
    expires_at: datetime
    created_at: datetime


class GitHubAuthResponse(BaseModel):
    redirect_url: str
