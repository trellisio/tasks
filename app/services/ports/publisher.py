from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypedDict

Payload = dict[str, Any] | str


class Events(TypedDict):
    channel: str
    payload: Payload


class Publisher(ABC):
    @abstractmethod
    async def publish(self, *, channel: str, payload: Payload) -> None:
        raise NotImplementedError
