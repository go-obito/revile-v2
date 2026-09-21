import logging
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _redact_database_url(value: str) -> str:
    scheme_separator = value.find("://")
    authority_start = scheme_separator + 3 if scheme_separator >= 0 else 0
    at_sign = value.find("@", authority_start)
    if at_sign < 0:
        return value

    userinfo = value[authority_start:at_sign]
    colon = userinfo.find(":")
    if colon < 0:
        return value
    return f"{value[:authority_start]}{userinfo[:colon]}:***{value[at_sign:]}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Revile API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://revile:revile@localhost:5432/revile"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    frontend_origin: str = "http://localhost:3000"
    imagekit_public_key: str = ""
    imagekit_private_key: str = ""
    imagekit_url_endpoint: str = ""
    cookie_secure: bool = False
    log_level: str = "INFO"
    public_dir: str = "public"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        raw_value = str(value)
        logger.debug("Raw DATABASE_URL before normalization: %r", _redact_database_url(raw_value))
        value = raw_value.strip()
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
