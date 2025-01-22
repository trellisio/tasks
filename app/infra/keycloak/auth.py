from typing import Literal

from keycloak import KeycloakOpenID
from kink import inject
from pydantic import Field
from pydantic_settings import BaseSettings

from app.services.ports.auth import Auth, Jwt


class KeycloakConfig(BaseSettings):
    KEYCLOAK_SERVER_URL: str = Field(
        description="URL for keycloak server",
        default="http://keycloak:8080/",
    )
    KEYCLOAK_REALM_NAME: str = Field(description="", default="trellis")
    KEYCLOAK_CLIENT_ID: str = Field(description="Keycloak client for auth", default="")
    KEYCLOAK_CLIENT_SECRET_KEY: str = Field(
        description="Keycloak secret for auth",
        default="",
    )


@inject(alias=Auth)
class KeycloakAuth(Auth):
    _client: KeycloakOpenID

    def __init__(self):
        config = KeycloakConfig()

        self._client = KeycloakOpenID(
            server_url=config.KEYCLOAK_SERVER_URL,
            realm_name=config.KEYCLOAK_REALM_NAME,
            client_id=config.KEYCLOAK_CLIENT_ID,
            client_secret_key=config.KEYCLOAK_CLIENT_SECRET_KEY,
        )

    async def decode(self, *, token: str, validate: bool = True) -> Jwt:
        decoded_response = await self._client.a_decode_token(token, validate=validate)
        return self._convert_to_jwt(decoded_response)

    async def has_role(self, *, token: str, role: str) -> bool:
        jwt = await self.validate(token)
        if not jwt:
            return False

        roles = jwt["roles"]
        return role in roles

    async def has_roles(self, *, token: str, roles: list[str], op: Literal["and", "or"]) -> bool:
        jwt = await self.validate(token)
        if not jwt:
            return False

        user_roles = jwt["roles"]
        intersection = set(user_roles) & set(roles)
        return bool(intersection) if op == "or" else len(intersection) == len(roles)

    def _convert_to_jwt(self, payload: dict) -> Jwt:  # noqa: PLR6301
        email = payload.get("email")
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])

        if not email:
            msg = "Authentication failed. Email or roles was not in token"
            raise ValueError(msg)

        return {
            "email": email,
            "roles": roles,
        }
