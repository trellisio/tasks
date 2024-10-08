from keycloak import KeycloakOpenID
from kink import inject
from pydantic import Field
from pydantic_settings import BaseSettings

from app.services.ports.auth import Auth, Jwt, Token


class KeycloakConfig(BaseSettings):
    KEYCLOAK_SERVER_URL: str = Field(
        description="URL for keycloak server", default="http://keycloak:8080/"
    )
    KEYCLOAK_REALM_NAME: str = Field(description="", default="trellis")
    KEYCLOAK_CLIENT_ID: str = Field(description="Keycloak client for auth", default="")
    KEYCLOAK_CLIENT_SECRET_KEY: str = Field(
        description="Keycloak secret for auth", default=""
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

    async def login(self, email: str, password: str) -> Token:
        payload = await self._client.a_token(email, password)
        return self._validate_payload(payload)

    async def refresh_token(self, refresh_token: str) -> Token:
        payload = await self._client.a_refresh_token(refresh_token)
        return self._validate_payload(payload)

    async def validate(self, token: str) -> Jwt:
        decoded_response = await self._client.a_decode_token(token, validate=True)
        return self._convert_to_jwt(decoded_response)

    async def has_role(self, token: str, role: str) -> bool:
        jwt = await self.validate(token)
        if not jwt:
            return False

        roles = jwt["roles"]
        return role in roles

    def _validate_payload(self, payload: dict) -> Token:
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")

        if not access_token or not refresh_token:
            raise ValueError(
                "Authentication failed. Access token or refresh token not returned from client"
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def _convert_to_jwt(self, payload: dict) -> Jwt:
        email = payload.get("email", None)
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])

        if not email:
            raise ValueError("Authentication failed. Email or roles was not in token")

        return {
            "email": email,
            "roles": roles,
        }
