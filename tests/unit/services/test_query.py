import asyncio

import pytest

from app.domain import models
from app.infra.memory.cache import InMemoryCache
from app.infra.memory.publisher import InMemoryEventPublisher
from app.infra.sqlalchemy.query import SqlAlchemyQuery, SqlConnection
from tests.unit.services.test_uow import SqlAlchemyUowImpl


class SqlAlchemyQueryImpl(SqlAlchemyQuery):
    pass


class TestQuery:
    cache: InMemoryCache
    query: SqlAlchemyQueryImpl

    @pytest.fixture(autouse=True)
    async def set_up(self):
        # create database tables
        connection = SqlConnection()
        await connection.connect()
        self.cache = InMemoryCache()
        self.query = SqlAlchemyQueryImpl(connection, self.cache)
        self.uow = SqlAlchemyUowImpl(connection, InMemoryEventPublisher())
        await self._seed_model()

        yield

        await connection.close(cleanup=True)

    async def test_marked_method_results_are_cached(self):
        res = await self.cache.get(
            f"{self.query._cache_key_prefix}:list_users:skip:<default>:limit:<default>"
        )
        assert res is None

        await self.query.list_users()
        res = await self.cache.get(
            f"{self.query._cache_key_prefix}:list_users:skip:<default>:limit:<default>"
        )

        assert res is not None

    async def test_marked_methods_return_cached_results_if_exists(self):
        res = await self.query.list_users()
        assert res is not None

        # invalidate the cache
        async with self.uow:
            await self.uow.user_repository.add(models.User(email="emailfour@gmail.com"))
            await self.uow.commit()

        res = await self.query.list_users()  # returning cached (stale) data still
        assert res is not None
        assert len(res) == 3

    async def test_marked_methods_caches_expire_and_will_repopulate(self):
        self.query._ttl = 1  # specify a short ttl so cache will refresh

        res = await self.query.list_users()
        assert len(res) == 3

        await asyncio.sleep(1)

        # invalidate the cache
        async with self.uow:
            await self.uow.user_repository.add(models.User(email="emailfour@gmail.com"))
            await self.uow.commit()

        res = await self.query.list_users()
        assert len(res) == 4  # returning the newly entered item because cache expired

    async def _seed_model(self):
        async with self.uow:
            await self.uow.user_repository.add(models.User(email="email@gmail.com"))
            await self.uow.user_repository.add(models.User(email="emailtwo@gmail.com"))
            await self.uow.user_repository.add(
                models.User(email="emailthree@gmail.com")
            )
            await self.uow.commit()
