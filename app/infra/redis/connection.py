from kink import inject
from pydantic import Field
from pydantic_settings import BaseSettings
from redis.asyncio import Redis

from app.logger import logger

from ..connection import Connection


class RedisConnectionConfig(BaseSettings):
    REDIS_HOST: str = Field(description="Redis host URL", default="redis")
    REDIS_PORT: int = Field(description="Redis host port", default=6379)
    REDIS_PASSWORD: str = Field(description="Redis password", default="password")


@inject(alias=Connection)
class RedisConnection(Connection):
    rc: Redis

    async def connect(self):
        config = RedisConnectionConfig()
        rc = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            protocol=3,
            db=0,
            decode_responses=True,
        )

        self.rc = rc
        await rc.ping()

        logger.info("Redis connected 🚨")

    async def close(self, cleanup: bool = False):
        await self.rc.aclose()
