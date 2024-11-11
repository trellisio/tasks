from typing import Literal, cast

from kink import inject
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from app.domain.models import Task, TaskList, ports
from app.services.ports.uow import TaskListRepository, Uow

from .connection import SqlConnection


# DAOs
class SqlAlchemyTaskDao(ports.TaskDao):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def update_all_tasks_with_status(
        self,
        *,
        task_list_pk: int,
        status: str,
        migration_status: str,
    ) -> None:
        query = """
            UPDATE task
            SET status = :migration_status
            WHERE task_list_id = :list_id AND status = :status
        """
        await self.session.execute(
            text(query),
            {"migration_status": migration_status, "list_id": task_list_pk, "status": status},
        )


# Repositories
class SqlAlchemyTaskListRepository(TaskListRepository):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, task_list: TaskList) -> None:
        self.session.add(task_list)

    async def add_tasks(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.session.add(task)

    async def find(self, pk: int) -> list[TaskList]:
        stmt = select(TaskList).where(TaskList._pk == pk)  # type: ignore[arg-type]  # noqa: SLF001
        res = await self.session.execute(stmt)
        return cast(list[TaskList], res.scalars().all())

    async def find_by_name(self, name: str) -> list[TaskList]:
        stmt = select(TaskList).where(TaskList._name == name)  # type: ignore[arg-type]  # noqa: SLF001
        res = await self.session.execute(stmt)
        return cast(list[TaskList], res.scalars().all())


@inject(alias=Uow, use_factory=True)
class SqlAlchemyUow(Uow):
    # repositories
    task_list_repository: SqlAlchemyTaskListRepository

    # DAOs
    task_dao: SqlAlchemyTaskDao

    # Internals
    _isolation_level: Literal["REPEATABLE READ", "READ COMMITTED"]
    _session: AsyncSession
    _default_session_factory: async_sessionmaker[AsyncSession]
    _rr_session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, connection: SqlConnection):
        super().__init__()
        def_engine = connection.default_engine
        rr_engine = connection.repeatable_read_engine

        self._default_session_factory = async_sessionmaker(
            def_engine,
            expire_on_commit=False,
        )

        self._rr_session_factory = async_sessionmaker(
            rr_engine,
            expire_on_commit=False,
        )

    async def __aenter__(self):
        session_factory = self._get_session_factory()
        async with session_factory() as session, session.begin():
            self._session = session
            self.task_list_repository = SqlAlchemyTaskListRepository(session)
            self.task_dao = SqlAlchemyTaskDao(session)

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
    ) -> async_sessionmaker[AsyncSession]:
        if self._isolation_level == "REPEATABLE READ":
            return self._rr_session_factory
        return self._default_session_factory
