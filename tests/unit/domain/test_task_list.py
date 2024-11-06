import pytest

from app.domain.models.task import Task
from app.domain.models.task_list import ARCHIVED_STATUS, ArchivedStatusError, InvalidStatusError, TaskDao, TaskList


class InMemoryTaskDao(TaskDao):
    tasks: list[Task]

    def __init__(self, task_list: TaskList):
        self.tasks = [
            Task(task_list=task_list, title="example", status="ready", description="task 1"),
            Task(task_list=task_list, title="example", status="ready", description="task 2"),
            Task(task_list=task_list, title="example", status="working", description="task 3"),
            Task(task_list=task_list, title="example", status="nonsense", description="task 4"),
        ]

    async def update_all_tasks_with_status(
        self,
        *,
        task_list_pk: int,  # noqa: ARG002
        status: str,
        migration_status: str,
    ) -> None:
        tasks = [task for task in self.tasks if task.status == status]
        for task in tasks:
            task.status = migration_status


class TestTaskList:
    task_list: TaskList

    @pytest.fixture(autouse=True)
    def _set_up(self) -> None:
        self.task_list = TaskList(name="todo", pk=1)

    def test_can_add_status_to_list(self) -> None:
        self.task_list.add_status("ready")

        assert isinstance(self.task_list.statuses, set)
        assert "ready" in self.task_list.statuses

    def test_default_status_must_be_one_of_the_statuses(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")

        self.task_list.default_status = "ready"
        assert self.task_list.default_status == "ready"

        with pytest.raises(InvalidStatusError):
            self.task_list.default_status = "backlog"

        with pytest.raises(InvalidStatusError):
            TaskList(
                name="todo",
                statuses={"ready", "working", "done"},
                default_status="backlog",
            )

        with pytest.raises(InvalidStatusError):
            TaskList(
                name="todo",
                statuses=None,
                default_status="backlog",
            )

    def test_archived_status_added_to_all_lists(self) -> None:
        assert ARCHIVED_STATUS in self.task_list.statuses

    def test_statuses_are_unique(self) -> None:
        assert len(self.task_list.statuses) == 1
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")

        expected_status_count = 4
        assert len(self.task_list.statuses) == expected_status_count
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")
        assert len(self.task_list.statuses) == expected_status_count

    async def test_can_remove_status_from_list(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("nonsense")

        dao = InMemoryTaskDao(self.task_list)
        self.task_list.add_status("READY")
        await self.task_list.remove_status(status="READY", dao=dao)

        assert isinstance(self.task_list.statuses, set)
        assert "READY" not in self.task_list.statuses
        assert "READY" not in self.task_list.statuses

    async def test_tasks_in_list_are_deleted_when_status_is_removed_with_no_mapping(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("nonsense")

        dao = InMemoryTaskDao(self.task_list)
        self.task_list.add_status("nonsense")
        await self.task_list.remove_status(status="nonsense", dao=dao)

        assert "nonsense" not in [task.status for task in dao.tasks]

    async def test_tasks_in_list_are_updated_when_status_is_removed_with_mapping(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("nonsense")

        dao = InMemoryTaskDao(self.task_list)
        self.task_list.add_status("nonsense")
        await self.task_list.remove_status(status="nonsense", dao=dao, migration_status="ready")

        assert "nonsense" not in [task.status for task in dao.tasks]
        assert len([task.status for task in dao.tasks if task.status == "ready"]) == 3

    async def test_tasks_in_list_are_updated_to_archived_when_no_migration_status_passed(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("nonsense")

        dao = InMemoryTaskDao(self.task_list)
        self.task_list.add_status("nonsense")
        await self.task_list.remove_status(status="nonsense", dao=dao)

        assert len([task.status for task in dao.tasks if task.status == ARCHIVED_STATUS]) == 1

    async def test_archived_status_cannot_be_removed(self) -> None:
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("nonsense")

        dao = InMemoryTaskDao(self.task_list)
        with pytest.raises(ArchivedStatusError):
            await self.task_list.remove_status(status=ARCHIVED_STATUS, dao=dao, migration_status="ready")
