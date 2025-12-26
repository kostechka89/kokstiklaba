from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        avatar=payload.avatar,
        is_verified_author=payload.is_verified_author,
        is_admin=payload.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_oauth_user(db: Session, name: str, email: str, avatar: str | None = None) -> User:
    user = User(
        name=name,
        email=email,
        hashed_password=None,
        avatar=avatar,
        is_verified_author=False,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
