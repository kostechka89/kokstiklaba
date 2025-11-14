from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, role_required
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate
from app.utils.context import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic], dependencies=[Depends(role_required(author=True))])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserPublic]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserPublic.from_orm(user) for user in users]


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserPublic:
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.from_orm(user)


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(role_required(author=True))])
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserPublic:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.from_orm(user)


@router.patch("/{user_id}", response_model=UserPublic, dependencies=[Depends(role_required(allow_admin=True))])
async def update_user(user_id: UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> UserPublic:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserPublic.from_orm(user)


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.dict(exclude_unset=True, exclude={"is_author", "is_admin"}).items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserPublic.from_orm(user)
