from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    database_url: str = Field(validation_alias="DATABASE_URL")
    secret_key: str = Field(validation_alias="SECRET_KEY")
    hash_scheme: str = Field(default="argon2", validation_alias="HASH_SCHEME")
    port: int = Field(default=8000, validation_alias="PORT")
    argon2_time_cost: int = Field(default=2, validation_alias="ARGON2_TIME_COST")
    argon2_memory_cost: int = Field(default=512, validation_alias="ARGON2_MEMORY_COST")
    argon2_parallelism: int = Field(default=2, validation_alias="ARGON2_PARALLELISM")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
