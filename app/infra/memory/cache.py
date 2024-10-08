import asyncio
from typing import Any, Mapping

from kink import inject

from app.services.ports.cache import Cache


@inject(alias=Cache)
class InMemoryCache(Cache):
    store: dict[str, Any]

    def __init__(self):
        self.store = {}

    async def get(self, key: str) -> str | None:
        result = self.store.get(key, None)
        if result:
            return str(result)
        return None

    async def multi_get(self, keys: list[str]) -> list[str | None]:
        return [self.store.get(key, None) for key in keys]

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        self.store[key] = value
        if ttl:
            asyncio.create_task(self._delete_with_delay(key, ttl))

        return True

    async def multi_set(self, values: Mapping[str, str]) -> bool:
        for key, value in values.items():
            self.store[key] = value
        return True

    async def delete(self, key: str) -> bool:
        return await self.multi_delete([key])

    async def multi_delete(self, keys: list[str]) -> bool:
        for key in keys:
            result = self.store.pop(key, False)
            if result is False:
                return False
        return True

    async def _delete_with_delay(self, key: str, ttl: int):
        await asyncio.sleep(ttl)
        await self.delete(key)
