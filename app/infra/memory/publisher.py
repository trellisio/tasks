from __future__ import annotations

from typing import Mapping

from kink import inject

from app.services.ports.publisher import Payload, Publisher


@inject(alias=Publisher)
class InMemoryEventPublisher(Publisher):
    published_messages: list[Mapping[str, Payload]]

    def __init__(self):
        self.published_messages = []

    async def publish(self, *, channel: str, payload: Payload) -> None:
        self.published_messages.append({"channel": channel, "payload": payload})
