"""Application settings loaded from environment variables (see .env.example)."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Insumap API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://insumap:insumap@localhost:5432/insumap"
    # Direct (non-pooled) connection for migrations; Neon provides it as DATABASE_URL_UNPOOLED.
    database_url_unpooled: str = ""

    jwt_secret: str = "change-me-in-production-please-32b"
    jwt_algorithm: str = "HS256"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 7
    delegated_token_minutes: int = 2

    refresh_cookie_name: str = "insumap_rt"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"

    login_max_attempts: int = 5
    login_window_minutes: int = 15
    assistant_messages_per_hour: int = 20

    state_cache_capacity: int = 128
    state_cache_ttl_seconds: int = 300

    cron_token: str = "change-me-cron"
    scheduler_enabled: bool = True

    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:insumap@example.com"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Insumap <no-reply@insumap.local>"

    ai_service_url: str = ""
    ai_service_token: str = ""
    ai_timeout_seconds: float = 20.0

    seed_demo_users: bool = True

    @field_validator("database_url", "database_url_unpooled")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        """Accept the plain ``postgres(ql)://`` URLs given by Neon/Render and use psycopg 3."""
        for prefix in ("postgresql://", "postgres://"):
            if v.startswith(prefix):
                return "postgresql+psycopg://" + v[len(prefix) :]
        return v

    @property
    def migration_url(self) -> str:
        return self.database_url_unpooled or self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
