import pytest

from app.domain import models
from app.infra.sqlalchemy.uow import SqlAlchemyUow, SqlConnection


class TestSqlAlchemyUow:
    uow: SqlAlchemyUow

    @pytest.fixture(autouse=True)
    async def set_up(self):  # noqa: PT004, ANN201
        # create database tables
        connection = SqlConnection()
        await connection.connect()
        self.uow = SqlAlchemyUow(connection=connection)
        await self._seed_model(name="test")

        yield

        await connection.close(cleanup=True)

    async def _seed_model(self, *, name: str) -> None:
        async with self.uow:
            task_list = models.TaskList(name=name)
            await self.uow.task_list_repository.add(task_list)
            await self.uow.commit()

    async def test_can_insert_model(self) -> None:
        await self._seed_model(name="tester")

    async def test_can_find_repos_by_pk(self) -> None:
        async with self.uow:
            pk: int = (await self.uow.task_list_repository.find_by_name(name="test"))[0].pk
            tasks_lists = await self.uow.task_list_repository.find(pk)
            assert len(tasks_lists) == 1
            assert tasks_lists[0].pk == pk

    async def test_can_find_repos_by_name(self) -> None:
        async with self.uow:
            tasks_lists = await self.uow.task_list_repository.find_by_name(name="test")
            assert len(tasks_lists) == 1
            assert tasks_lists[0].name == "test"

    async def test_can_rollback(self) -> None:
        async with self.uow:
            task_list = models.TaskList(name="TODO")
            await self.uow.task_list_repository.add(task_list)
            await self.uow.rollback()

        async with self.uow:
            task_lists = await self.uow.task_list_repository.find_by_name(name="TODO")
            assert task_lists == []

    async def test_rollback_occurs_when_commit_not_called(self) -> None:
        async with self.uow:
            task_list = models.TaskList(name="TODO")
            await self.uow.task_list_repository.add(task_list)

        async with self.uow:
            task_lists = await self.uow.task_list_repository.find_by_name(name="TODO")
            assert task_lists == []

    async def test_rollback_occurs_when_error_is_raised(self) -> None:
        try:
            async with self.uow:
                task_list = models.TaskList(name="TODO")
                await self.uow.task_list_repository.add(task_list)
                raise Exception("Error")  # noqa: TRY301, TRY002, EM101
        except Exception:  # noqa: BLE001, S110
            pass

        async with self.uow:
            task_lists = await self.uow.task_list_repository.find_by_name("TODO")
            assert task_lists == []
