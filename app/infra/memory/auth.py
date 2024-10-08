from kink import inject

from app.services.ports.auth import Auth, Jwt, Token


@inject(alias=Auth)
class InMemoryAuth(Auth):
    _validation_outcome: bool
    _role_outcome: bool

    def __init__(self):
        self._validation_outcome = True
        self._role_outcome = True

    async def login(self, email: str, password: str) -> Token:
        return {"access_token": "", "refresh_token": ""}

    async def refresh_token(self, refresh_token: str) -> Token:
        return {"access_token": "", "refresh_token": ""}

    async def validate(self, token: str) -> Jwt:
        if self._validation_outcome:
            return {"email": "fake-email@gmail.com", "roles": ["admin", "test"]}
        raise ValueError("Authentication validation failed")

    async def has_role(self, role: str) -> bool:
        if self._role_outcome:
            return True
        return False
