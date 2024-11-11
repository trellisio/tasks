from typing import Mapping

from kink import inject
from redis.asyncio import Redis

from app.services.ports.cache import Cache

from .connection import RedisConnection


@inject(alias=Cache)
class RedisCache(Cache):
    rc: Redis

    def __init__(self, connection: RedisConnection):
        self.rc = connection.rc

    async def get(self, key: str) -> str | None:
        return await self.rc.get(key)

    async def multi_get(self, keys: list[str]) -> list[str | None]:
        return await self.rc.mget(keys)

    async def set(self, *, key: str, value: str, ttl: int | None = None) -> bool:
        value = str(value)
        ok = await self.rc.set(key, value, ex=ttl)
        return bool(ok)

    async def multi_set(self, values: Mapping[str, str]) -> bool:
        vals: Mapping[str | bytes, str] = {k: str(v) for k, v in values.items()}

        ok = await self.rc.mset(vals)
        return bool(ok)

    async def delete(self, key: str) -> bool:
        return await self.multi_delete([key])

    async def multi_delete(self, keys: list[str]) -> bool:
        ok = await self.rc.delete(*keys)
        return bool(ok)
