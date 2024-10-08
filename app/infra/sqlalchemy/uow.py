from typing import Literal, cast

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from app.domain import models
from app.services.ports import Publisher
from app.services.ports.uow import Uow, UserRepository

from .connection import SqlConnection


class SqlAlchemyUserRepository(UserRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, user: models.User):
        self.session.add(user)

    async def find(self, email: str) -> list[models.User]:
        stmt = select(models.User).where(models.User.email == email)  # type: ignore
        res = await self.session.execute(stmt)
        return cast(list[models.User], res.scalars().all())

    async def remove(self, email: str) -> list[models.User]:
        stmt = select(models.User).where(models.User.email == email)  # type: ignore
        res = await self.session.execute(stmt)
        users = cast(list[models.User], res.scalars().all())

        for user in users:
            await self.session.delete(user)

        return users


@inject(alias=Uow, use_factory=True)
class SqlAlchemyUow(Uow):
    # repositories
    user_repository: SqlAlchemyUserRepository

    # Internals
    _isolation_level: Literal["REPEATABLE READ"] | Literal["READ COMMITTED"]
    _session: AsyncSession
    _rr_session_factory: async_sessionmaker[AsyncSession]
    _rc_session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, connection: SqlConnection, publisher: Publisher):
        super().__init__(publisher)
        rr_engine = connection.repeatable_read_engine
        def_engine = connection.default_engine

        self._rr_session_factory = async_sessionmaker(
            rr_engine,
            expire_on_commit=False,
        )
        self._default_session_factory = async_sessionmaker(
            def_engine,
            expire_on_commit=False,
        )

    async def __aenter__(self):
        session_factory = self._get_session_factory("DEFAULT")
        async with session_factory() as session:
            async with session.begin():
                self._session = session
                self.user_repository = SqlAlchemyUserRepository(session)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        # if nothing to rollback, nothing will happen
        await self._session.rollback()

    async def close(self):
        await self._session.close()

    # Internals
    def _get_session_factory(
        self, isolation_level: Literal["DEFAULT"] | Literal["REPEATABLE READ"]
    ):
        if isolation_level == "REPEATABLE READ":
            return self._rr_session_factory
        else:
            return self._default_session_factory
