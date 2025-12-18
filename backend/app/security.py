from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(
    schemes=["argon2" if settings.hash_scheme == "argon2" else settings.hash_scheme],
    deprecated="auto",
    argon2__time_cost=settings.argon2_time_cost,
    argon2__memory_cost=settings.argon2_memory_cost,
    argon2__parallelism=settings.argon2_parallelism,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)
