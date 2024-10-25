from abc import ABC, abstractmethod
from typing import TypedDict

from app.domain.event import Payload


class Events(TypedDict):
    channel: str
    payload: Payload


class Publisher(ABC):
    @abstractmethod
    async def publish(self, *, channel: str, payload: Payload) -> None:
        raise NotImplementedError
