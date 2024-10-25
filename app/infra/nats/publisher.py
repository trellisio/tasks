import json

from kink import inject
from nats.aio.client import Client

from app.services.ports.publisher import Payload, Publisher

from .connection import NatsConnection


@inject(alias=Publisher)
class NatsEventPublisher(Publisher):
    nc: Client

    def __init__(self, connection: NatsConnection):
        self.nc = connection.nc

    async def publish(self, *, channel: str, payload: Payload) -> None:
        # if payload is dict, turn to string and decode
        if isinstance(payload, dict):
            payload = json.dumps(payload)  # turn to string

        await self.nc.publish(channel, payload.encode())
