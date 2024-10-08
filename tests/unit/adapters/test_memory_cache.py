import pytest

from app.infra.memory.cache import InMemoryCache


class TestInMemoryCache:
    cache: InMemoryCache

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.cache = InMemoryCache()

    async def test_can_set_value(self):
        res = await self.cache.set("service", "tasks")
        assert res is True
        assert self.cache.store.get("service", None) == "tasks"

    async def test_can_set_values(self):
        res = await self.cache.multi_set(
            {"service": "tasks", "name": "developer", "company": "trellis"}
        )
        assert res is True

    async def test_can_cache_value(self):
        await self.cache.set("service", "tasks")
        res = await self.cache.get("service")
        assert res == "tasks"

    async def test_can_cache_values(self):
        await self.cache.multi_set(
            {"service": "tasks", "name": "developer", "company": "trellis"}
        )
        res = await self.cache.get("service")
        assert res == "tasks"
        res = await self.cache.get("name")
        assert res == "developer"
        res = await self.cache.get("company")
        assert res == "trellis"

    async def test_can_delete_value(self):
        await self.cache.set("service", "tasks")
        await self.cache.delete("service")
        res = await self.cache.get("service")
        assert res is None

    async def test_can_delete_values(self):
        await self.cache.multi_set(
            {"service": "tasks", "name": "developer", "company": "trellis"}
        )
        await self.cache.multi_delete(["service", "name", "company"])
        res = await self.cache.get("service")
        assert res is None
        res = await self.cache.get("name")
        assert res is None
        res = await self.cache.get("company")
        assert res is None
