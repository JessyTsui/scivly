from typing import Annotated

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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
    app_url: str = Field(
        default="http://localhost:3100",
        validation_alias=AliasChoices("SCIVLY_APP_URL", "APP_URL", "NEXT_PUBLIC_APP_URL"),
    )
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
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3100",
            "http://localhost:3000",
        ]
    )
    auth_jwt_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_AUTH_JWT_SECRET", "AUTH_JWT_SECRET"),
    )
    auth_jwt_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_AUTH_JWT_KEY", "CLERK_JWT_KEY"),
    )
    auth_jwks_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_AUTH_JWKS_URL", "CLERK_JWKS_URL"),
    )
    auth_issuer: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_AUTH_ISSUER", "CLERK_ISSUER"),
    )
    auth_audience: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_AUTH_AUDIENCE", "CLERK_AUDIENCE"),
    )
    auth_authorized_parties: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3100"],
        validation_alias=AliasChoices("SCIVLY_AUTH_AUTHORIZED_PARTIES", "AUTH_AUTHORIZED_PARTIES"),
    )
    embedding_provider: str = Field(
        default="hash",
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_PROVIDER", "EMBEDDING_PROVIDER"),
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_MODEL", "EMBEDDING_MODEL"),
    )
    embedding_dimensions: int = Field(
        default=1536,
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_DIMENSIONS", "EMBEDDING_DIMENSIONS"),
    )
    embedding_api_base: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_API_BASE", "EMBEDDING_API_BASE"),
    )
    embedding_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_API_KEY", "EMBEDDING_API_KEY", "OPENAI_API_KEY"),
    )
    embedding_timeout_seconds: float = Field(
        default=20.0,
        validation_alias=AliasChoices("SCIVLY_EMBEDDING_TIMEOUT_SECONDS", "EMBEDDING_TIMEOUT_SECONDS"),
    )
    api_key_rate_limit_window_seconds: int = 60
    api_key_rate_limit_per_key: int = 60
    api_key_rate_limit_per_workspace: int = 300
    stripe_secret_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_SECRET_KEY", "STRIPE_SECRET_KEY"),
    )
    stripe_webhook_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_WEBHOOK_SECRET", "STRIPE_WEBHOOK_SECRET"),
    )
    stripe_pro_price_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_PRO_PRICE_ID", "STRIPE_PRO_PRICE_ID"),
    )
    stripe_checkout_success_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_CHECKOUT_SUCCESS_URL", "STRIPE_CHECKOUT_SUCCESS_URL"),
    )
    stripe_checkout_cancel_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_CHECKOUT_CANCEL_URL", "STRIPE_CHECKOUT_CANCEL_URL"),
    )
    stripe_portal_return_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SCIVLY_STRIPE_PORTAL_RETURN_URL", "STRIPE_PORTAL_RETURN_URL"),
    )
    billing_free_papers_per_day: int = 10
    billing_free_llm_tokens_per_month: int = 50_000
    billing_free_digests_per_month: int = 10
    billing_pro_papers_per_day: int = 250
    billing_pro_llm_tokens_per_month: int = 1_000_000
    billing_pro_digests_per_month: int = 200

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("auth_authorized_parties", mode="before")
    @classmethod
    def split_authorized_parties(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator(
        "app_url",
        "stripe_checkout_success_url",
        "stripe_checkout_cancel_url",
        "stripe_portal_return_url",
        mode="before",
    )
    @classmethod
    def normalize_urls(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()
        return stripped.rstrip("/") if stripped else None

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
