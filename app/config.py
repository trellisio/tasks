from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

Environment = Literal["local", "test", "dev", "stg", "prd"]


class BasesConfig(BaseSettings):
    ENVIRONMENT: Environment = Field(
        description="Environment process is running in", default="local"
    )
    CACHE_TTL: int | None = Field(
        description="TTL for key expiration in cache", default=None
    )
    # Keycloak
    KEYCLOAK_SERVER_URL: str = Field(
        description="URL for keycloak server", default="http://keycloak:8080/"
    )
    KEYCLOAK_REALM_NAME: str = Field(description="", default="trellis")
    KEYCLOAK_CLIENT_ID: str = Field(description="Keycloak client for auth", default="")
    KEYCLOAK_CLIENT_SECRET_KEY: str = Field(
        description="Keycloak secret for auth", default=""
    )


config = BasesConfig()
