from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from argon2 import PasswordHasher
from jose import JWTError, jwt

from app.core.config import get_settings


password_hasher = PasswordHasher()
settings = get_settings()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except Exception:
        return False


def create_token(subject: str, session_id: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": subject, "exp": expire, "session_id": session_id}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None


def generate_session_id() -> str:
    return uuid4().hex
