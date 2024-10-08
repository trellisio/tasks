import pytest

from app.domain import models
from app.infra.memory.publisher import InMemoryEventPublisher
from app.infra.sqlalchemy.uow import SqlAlchemyUow, SqlConnection


class TestSqlDb:
    uow: SqlAlchemyUow

    @pytest.fixture(autouse=True)
    async def set_up(self):
        connection = SqlConnection()
        await connection.connect()
        self.uow = SqlAlchemyUow(connection, InMemoryEventPublisher())
        await self._seed_model()

        yield

        await connection.close(cleanup=True)

    async def test_can_insert_model(self):
        await self._seed_model("another_email@gmail.com")

    async def test_can_select_model(self):
        async with self.uow:
            users = await self.uow.user_repository.find(email="email@gmail.com")
            assert users is not None
            assert users != []
            assert len(users) == 1
            user = users[0]
            assert user.email == "email@gmail.com"

    async def test_can_remove_model(self):
        async with self.uow:
            await self.uow.user_repository.remove("email@gmail.com")
            await self.uow.commit()

        async with self.uow:
            users = await self.uow.user_repository.find(email="email@gmail.com")
            assert users == []

    async def test_can_rollback(self):
        async with self.uow:
            user = models.User(email="another_email@gmail.com")
            await self.uow.user_repository.add(user)
            await self.uow.rollback()

        async with self.uow:
            users = await self.uow.user_repository.find(email="another_email@gmail.com")
            assert users == []

    async def test_rollback_occurs_when_commit_not_called(self):
        async with self.uow:
            user = models.User(email="another_email@gmail.com")
            await self.uow.user_repository.add(user)

        async with self.uow:
            users = await self.uow.user_repository.find(email="another_email@gmail.com")
            assert users == []

    async def test_rollback_occurs_when_error_is_raised(self):
        try:
            async with self.uow:
                user = models.User(email="another_email@gmail.com")
                await self.uow.user_repository.add(user)
                raise Exception("Error")
        except Exception:
            pass

        async with self.uow:
            users = await self.uow.user_repository.find(email="another_email@gmail.com")
            assert users == []

    async def _seed_model(self, email: str = "email@gmail.com"):
        async with self.uow:
            user = models.User(email=email)
            await self.uow.user_repository.add(user)
            await self.uow.commit()
