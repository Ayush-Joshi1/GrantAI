from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Runtime
    app_env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # API
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    api_title: str = Field(default="Grant Agent API", alias="API_TITLE")
    api_description: str = Field(
        default="AI platform for grant discovery, eligibility checks, and proposal generation.",
        alias="API_DESCRIPTION",
    )
    api_version: str = Field(default="1.0.0", alias="API_VERSION")

    # Observability
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    correlation_id_header: str = Field(default="X-Request-Id", alias="CORRELATION_ID_HEADER")

    # IBM watsonx Orchestrate
    orchestrate_api_key: str | None = Field(default=None, alias="WATSONX_ORCHESTRATE_API_KEY")
    orchestrate_url: str | None = Field(default=None, alias="WATSONX_ORCHESTRATE_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

