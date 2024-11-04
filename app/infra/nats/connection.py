from kink import inject
from nats import connect
from nats.aio.client import Client
from pydantic import Field
from pydantic_settings import BaseSettings

from app.logger import logger

from ..connection import Connection


class NatsConnectionConfig(BaseSettings):
    NATS_URL: str = Field(description="NATS connection URL", default="nats://nats:4222")


@inject(alias=Connection)
class NatsConnection(Connection):
    nc: Client

    async def connect(self) -> None:
        config = NatsConnectionConfig()
        nc = await connect(config.NATS_URL)

        self.nc = nc
        logger.info("Nats connected 🚨")

    async def close(self, *, cleanup: bool = False) -> None:  # noqa: ARG002
        await self.nc.close()
