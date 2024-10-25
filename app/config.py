from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

Environment = Literal["local", "test", "dev", "stg", "prd"]


class BasesConfig(BaseSettings):
    ENVIRONMENT: Environment = Field(
        description="Environment process is running in",
        default="local",
    )
    CACHE_TTL: int | None = Field(
        description="TTL for key expiration in cache",
        default=None,
    )


config = BasesConfig()
