from typing import cast

import pytest
from sqlalchemy.future import select

from app.domain import models
from app.domain.models.user import DomainEvent
from app.infra.memory.publisher import InMemoryEventPublisher
from app.infra.sqlalchemy.uow import (
    SqlAlchemyUow,
    SqlAlchemyUserRepository,
    SqlConnection,
)


class SqlAlchemyUserRepositoryImpl(SqlAlchemyUserRepository):
    async def find_by_email(self, email: str) -> list[models.User]:
        stmt = select(models.User).where(models.User.email == email)  # type: ignore
        res = await self.session.execute(stmt)
        return cast(list[models.User], res.scalars().all())

    async def remove_by_email(self, email: str) -> list[models.User]:
        stmt = select(models.User).where(models.User.email == email)  # type: ignore
        res = await self.session.execute(stmt)
        users = cast(list[models.User], res.scalars().all())

        for user in users:
            await self.session.delete(user)

        return users


class SqlAlchemyUowImpl(SqlAlchemyUow):
    user_repository: SqlAlchemyUserRepositoryImpl

    async def __aenter__(self):
        async with self._default_session_factory() as session:
            async with session.begin():
                self._session = session
                self.user_repository = SqlAlchemyUserRepositoryImpl(session)


class TestRepository:
    uow: SqlAlchemyUowImpl

    @pytest.fixture(autouse=True)
    async def set_up(self):
        # create database tables
        connection = SqlConnection()
        await connection.connect()
        self.uow = SqlAlchemyUowImpl(connection, InMemoryEventPublisher())
        await self._seed_model()

        yield

        await connection.close(cleanup=True)

    async def test_find_methods_have_objects_added_to_seen(self):
        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            assert len(users) == 1
            assert set(users) == self.uow.user_repository.seen

        async with self.uow:
            users = await self.uow.user_repository.find(email="email@gmail.com")
            assert len(users) == 1
            assert set(users) == self.uow.user_repository.seen

    async def test_remove_methods_have_objects_added_to_seen(self):
        async with self.uow:
            users = await self.uow.user_repository.remove_by_email(
                email="email@gmail.com"
            )
            assert len(users) == 1
            assert set(users) == self.uow.user_repository.seen

    async def test_add_methods_have_objects_added_to_seen(self):
        async with self.uow:
            user = models.User(email="some-email@gmail.com")
            await self.uow.user_repository.add(user)
            assert set([user]) == self.uow.user_repository.seen

    async def _seed_model(self, email: str = "email@gmail.com"):
        async with self.uow:
            user = models.User(email=email)
            await self.uow.user_repository.add(user)
            await self.uow.commit()


class TestUow:
    uow: SqlAlchemyUowImpl
    publisher: InMemoryEventPublisher

    @pytest.fixture(autouse=True)
    async def set_up(self):
        # create database tables
        connection = SqlConnection()
        await connection.connect()
        self.publisher = InMemoryEventPublisher()
        self.uow = SqlAlchemyUowImpl(connection, self.publisher)
        await self._seed_model()

        yield

        await connection.close(cleanup=True)

    async def test_domain_events_are_published(self):
        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            assert len(users) == 1
            user = users[0]
            user.some_domain_method()
            assert user.events == [DomainEvent("email@gmail.com")]
            await self.uow.commit()

            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "email@gmail.com"},
                }
            ]

    async def test_aggregate_versions_are_auto_incremented(self):
        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            assert len(users) == 1
            user = users[0]
            user.some_domain_method()

        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            assert len(users) == 1
            user = users[0]
            assert user.version == 1

    async def test_calling_commit_twice_wont_increment_version_twice(self):
        async with self.uow:
            user = models.User(email="another_email@gmail.com")
            await self.uow.user_repository.add(user)
            await self.uow.commit()

            try:
                await self.uow.commit()
            except Exception:
                pass

        async with self.uow:
            users = await self.uow.user_repository.find(email="another_email@gmail.com")
            assert len(users) == 1
            user = users[0]
            assert user.version == 1

    async def test_calling_commit_twice_wont_raise_domain_event_twice(self):
        async with self.uow:
            user = models.User(email="another_email@gmail.com")
            await self.uow.user_repository.add(user)
            user.some_domain_method()
            await self.uow.commit()

            try:
                await self.uow.commit()
            except Exception:
                pass

        async with self.uow:
            users = await self.uow.user_repository.find(email="another_email@gmail.com")
            assert len(users) == 1
            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "another_email@gmail.com"},
                }
            ]

    async def test_seen_aggregates_restart_on_each_session(self):
        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            assert users == list(self.uow.user_repository.seen)

        async with self.uow:
            assert list(self.uow.user_repository.seen) == []

    async def test_objects_that_are_edited_after_commit_are_committed_on_second_commit(
        self,
    ):
        async with self.uow:
            users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            user = users[0]
            user.some_domain_method()
            await self.uow.commit()

            assert user.version == 2
            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "email@gmail.com"},
                }
            ]

            new_user = models.User(email="another_email@gmail.com")
            await self.uow.user_repository.add(new_user)
            new_user.some_domain_method()
            await self.uow.commit()

            assert new_user.version == 1
            assert user.version == 2
            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "email@gmail.com"},
                },
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "another_email@gmail.com"},
                },
            ]

            await self.uow.commit()

            assert new_user.version == 1
            assert user.version == 2
            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "email@gmail.com"},
                },
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "another_email@gmail.com"},
                },
            ]

            old_users = await self.uow.user_repository.find_by_email(
                email="email@gmail.com"
            )
            old_user = old_users[0]
            await self.uow.commit()

            assert (
                old_user.version == 3
            )  # NOTE that will increase because was fetched through repo
            assert self.publisher.published_messages == [
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "email@gmail.com"},
                },
                {
                    "channel": "DomainThingHappened",
                    "payload": {"email": "another_email@gmail.com"},
                },
            ]

    async def _seed_model(self, email: str = "email@gmail.com"):
        async with self.uow:
            user = models.User(email=email)
            await self.uow.user_repository.add(user)
            await self.uow.commit()
