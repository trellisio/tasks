from typing import Literal

from kink import inject

from app.services.ports.auth import Auth, Jwt


@inject(alias=Auth)
class InMemoryAuth(Auth):
    _validation_outcome: bool
    _role_outcome: bool

    def __init__(self):
        self._validation_outcome = True
        self._role_outcome = True

    async def decode(self, *, token: str, validate: bool = True) -> Jwt:  # noqa: ARG002
        if self._validation_outcome:
            return {"email": "fake-email@gmail.com", "roles": ["admin", "test"]}
        msg = "Authentication validation failed"
        raise ValueError(msg)

    async def has_role(self, *, token: str, role: str) -> bool:  # noqa: ARG002
        return bool(self._role_outcome)

    async def has_roles(self, *, token: str, roles: list[str], op: Literal["and", "or"]) -> bool:  # noqa: ARG002
        return bool(self._role_outcome)
