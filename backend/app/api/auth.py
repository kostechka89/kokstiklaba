from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, Token, RefreshRequest, SessionInfo
from app.schemas.user import UserCreate, UserRead
from app.crud.users import create_user, get_user_by_email
from app.core.security import verify_password, create_token
from app.core.config import get_settings
from app.db.session import get_db
from app.services.sessions import session_store
from app.api.deps import get_current_user
from app.services.metrics import USERS_CREATED

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    user = create_user(db, payload)
    USERS_CREATED.inc()
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    settings = get_settings()
    session_id = session_store.create(user.id, request.headers.get("user-agent", "unknown"))
    access_token = create_token(str(user.id), timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token(
        str(user.id),
        timedelta(minutes=settings.refresh_token_expire_minutes),
        extra={"sid": session_id},
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest):
    settings = get_settings()
    try:
        claims = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=["HS256"])
        user_id = claims.get("sub")
        session_id = claims.get("sid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if not session_id or not session_store.get(session_id):
        raise HTTPException(status_code=401, detail="Session not found")
    access_token = create_token(str(user_id), timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token(
        str(user_id),
        timedelta(minutes=settings.refresh_token_expire_minutes),
        extra={"sid": session_id},
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(payload: RefreshRequest):
    settings = get_settings()
    try:
        claims = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    session_id = claims.get("sid")
    if session_id:
        session_store.delete(session_id)
    return {"status": "logged_out"}


@router.get("/sessions", response_model=list[SessionInfo])
def list_sessions(current_user=Depends(get_current_user)):
    return session_store.list_for_user(current_user["id"])
