from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .logger import configure_logging, logger
from .models import User
from .schemas import MessageResponse, RegisterRequest
from .security import hash_password

configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth MVP", version="0.1.0")


@app.post("/api/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    hashed = hash_password(payload.password)
    user = User(login=payload.login, password_hash=hashed)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        logger.warning("registration_conflict", login=payload.login)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists",
        )

    logger.info("registration_success", user_id=user.id, login=payload.login)
    return MessageResponse(message="user создан")


@app.get("/healthz")
def healthcheck():
    return {"status": "ok", "env": settings.app_env}
