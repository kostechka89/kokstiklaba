from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "News Platform"
    api_prefix: str = "/api"
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(60 * 24 * 7, env="REFRESH_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    github_client_id: str = Field(..., env="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(..., env="GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = Field("http://localhost:8000/api/auth/github/callback", env="GITHUB_REDIRECT_URI")
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    news_cache_ttl_seconds: int = Field(300, env="NEWS_CACHE_TTL_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


BASE_DIR = Path(__file__).resolve().parent.parent
