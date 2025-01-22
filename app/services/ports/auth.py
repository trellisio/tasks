from abc import ABC, abstractmethod
from typing import Literal, TypedDict


class Jwt(TypedDict):
    user_id: str
    email: str
    roles: list[str]


class Token(TypedDict):
    access_token: str
    refresh_token: str


class Auth(ABC):
    @abstractmethod
    async def decode(self, *, token: str, validate: bool = True) -> Jwt:
        raise NotImplementedError

    @abstractmethod
    async def has_role(self, *, token: str, role: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def has_roles(self, *, token: str, roles: list[str], op: Literal["and", "or"]) -> bool:
        raise NotImplementedError
