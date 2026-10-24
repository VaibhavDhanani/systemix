from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables (and apps/api/.env locally)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["local", "test", "production"] = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://systemix:systemix@localhost:5442/systemix"
    redis_url: str = "redis://localhost:6389/0"
    health_check_timeout_seconds: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
