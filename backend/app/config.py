from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SCIVLY_",
        extra="ignore",
    )

    app_name: str = "Scivly API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8100
    database_url: str = Field(
        default="postgresql://localhost:5432/scivly",
        validation_alias=AliasChoices("SCIVLY_DATABASE_URL", "DATABASE_URL"),
    )
    database_echo: bool = False
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("SCIVLY_REDIS_URL", "REDIS_URL"),
    )
    run_migrations_on_startup: bool = False
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3100",
            "http://localhost:3000",
        ]
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
