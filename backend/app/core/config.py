from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TeamPulse Leave Management API"
    API_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = Field(
        default="postgresql+psycopg://localhost:5432/teampulse"
    )

    SUPABASE_URL: str = Field(default="https://your-project-ref.supabase.co")
    SUPABASE_PUBLISHABLE_KEY: str = Field(default="sb_publishable_replace_me")
    NEXT_PUBLIC_SUPABASE_URL: str | None = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = Field(default=None)
    SUPABASE_JWT_AUDIENCE: str = Field(default="authenticated")
    SUPABASE_AUTH_VERIFY_TIMEOUT_SECONDS: int = 5
    REQUIRE_EMAIL_VERIFICATION: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
