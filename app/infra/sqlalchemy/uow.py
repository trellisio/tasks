from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.ports.uow import TaskListRepository, TaskRepository, Uow

if TYPE_CHECKING:
    from app.domain import models
    from app.services.ports import Publisher

    from .connection import SqlConnection


class SqlAlchemyTaskListRepository(TaskListRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, task_list: models.TaskList) -> None:
        self.session.add(task_list)


class SqlAlchemyTaskRepository(TaskRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, task: models.Task) -> None:
        self.session.add(task)


@inject(alias=Uow, use_factory=True)
class SqlAlchemyUow(Uow):
    # repositories
    task_list_repository: SqlAlchemyTaskListRepository

    # Internals
    _isolation_level: Literal["REPEATABLE READ", "READ COMMITTED"]
    _session: AsyncSession
    _rr_session_factory: async_sessionmaker[AsyncSession]
    _rc_session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, *, connection: SqlConnection, publisher: Publisher):
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
        async with session_factory() as session, session.begin():
            self._session = session
            self.task_list_repository = SqlAlchemyTaskListRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        # if nothing to rollback, nothing will happen
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()

    # Internals
    def _get_session_factory(
        self,
        isolation_level: Literal["DEFAULT", "REPEATABLE READ"],
    ) -> None:
        if isolation_level == "REPEATABLE READ":
            return self._rr_session_factory
        return self._default_session_factory
