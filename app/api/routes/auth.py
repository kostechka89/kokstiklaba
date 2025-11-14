from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_sso.sso.github import GitHubSSO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    GitHubAuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SessionInfo,
    TokenPair,
)
from app.schemas.user import UserCreate, UserPublic
from app.services import auth as auth_service
from app.services.cache import delete_session, get_session, list_sessions
from app.services.security import decode_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
github_sso = GitHubSSO(settings.github_client_id, settings.github_client_secret, redirect_uri=settings.github_redirect_uri)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserPublic:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        avatar_url=payload.avatar_url,
        is_author=payload.is_author,
        is_admin=payload.is_admin,
        password_hash=hash_password(payload.password),
        registered_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserPublic.from_orm(user)


@router.post("/login", response_model=TokenPair)
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_agent = request.headers.get("user-agent", "unknown")
    token_pair, _ = await auth_service.create_token_pair(user, user_agent)
    return token_pair


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(request: Request, payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    token_data = decode_token(payload.refresh_token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    session = await get_session(token_data["session_id"])
    if not session or session.get("user_id") != token_data["sub"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    if session["expires_at"] < datetime.utcnow():
        await delete_session(token_data["session_id"])
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    result = await db.execute(select(User).where(User.id == UUID(token_data["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        await delete_session(token_data["session_id"])
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await delete_session(token_data["session_id"])

    user_agent = request.headers.get("user-agent", session.get("user_agent", "unknown"))
    token_pair, _ = await auth_service.create_token_pair(user, user_agent)
    return token_pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest) -> None:
    token_data = decode_token(payload.refresh_token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    await delete_session(token_data["session_id"])


@router.get("/sessions", response_model=list[SessionInfo])
async def get_sessions(current_user=Depends(get_current_user)) -> list[SessionInfo]:
    sessions_raw = await list_sessions(str(current_user.id))
    return [
        SessionInfo(
            session_id=session_id,
            user_agent=data.get("user_agent"),
            created_at=data["created_at"],
            expires_at=data["expires_at"],
        )
        for session_id, data in sessions_raw.items()
    ]


@router.get("/me", response_model=UserPublic)
async def get_me(current_user=Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        is_author=current_user.is_author,
        is_admin=current_user.is_admin,
        registered_at=current_user.registered_at,
    )


@router.get("/github/login", response_model=GitHubAuthResponse)
async def github_login() -> GitHubAuthResponse:
    redirect_url = github_sso.get_login_redirect()
    return GitHubAuthResponse(redirect_url=redirect_url)


@router.get("/github/callback", response_model=TokenPair)
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)) -> TokenPair:
    async with github_sso:
        user_info = await github_sso.verify_and_process(request)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GitHub auth failed")

    result = await db.execute(select(User).where(User.github_id == user_info.id))
    user = result.scalar_one_or_none()
    if not user:
        result = await db.execute(select(User).where(User.email == user_info.email))
        user = result.scalar_one_or_none()
    if not user:
        user = User(
            name=user_info.display_name or user_info.username,
            email=user_info.email,
            avatar_url=user_info.avatar,
            is_author=False,
            is_admin=False,
            password_hash=hash_password(github_sso.state or "temporary"),
            registered_at=datetime.utcnow(),
            github_id=user_info.id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.github_id:
        user.github_id = user_info.id
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user_agent = request.headers.get("user-agent", "github")
    token_pair, _ = await auth_service.create_token_pair(user, user_agent)
    return token_pair
