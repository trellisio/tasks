from abc import ABC, abstractmethod
from typing import TypedDict


class Jwt(TypedDict):
    email: str
    roles: list[str]


class Token(TypedDict):
    access_token: str
    refresh_token: str


class Auth(ABC):
    @abstractmethod
    async def login(self, email: str, password: str) -> Token:
        raise NotImplementedError()

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Token:
        raise NotImplementedError()

    @abstractmethod
    async def validate(self, token: str) -> Jwt:
        raise NotImplementedError()

    @abstractmethod
    async def has_role(self, role: str) -> bool:
        raise NotImplementedError()
