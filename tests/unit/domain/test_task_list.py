import pytest

from app.domain.models.task_list import InvalidStatus, TaskList, TaskRepository


class TaskRepositoryPlaceholder(TaskRepository):
    async def update_all_tasks_with_status(
        self, *, list_id: int, old_status: str, new_status: str
    ):
        return

    async def delete_all_tasks_with_status(self, *, list_id: int, status: str):
        return


class TestTaskList:
    task_list: TaskList

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.task_list = TaskList(identifier=1, name="todo")

    def test_can_add_status_to_list(self):
        self.task_list.add_status("ready")

        assert isinstance(self.task_list.statuses, set)
        assert "ready" in self.task_list.statuses

    def test_default_status_must_be_one_of_the_statuses(self):
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")

        self.task_list.default_status = "ready"
        assert self.task_list.default_status == "ready"

        with pytest.raises(InvalidStatus):
            self.task_list.default_status = "backlog"

        with pytest.raises(InvalidStatus):
            TaskList(
                identifier=1,
                name="todo",
                statuses={"ready", "working", "done"},
                default_status="backlog",
            )

        with pytest.raises(InvalidStatus):
            TaskList(
                identifier=1,
                name="todo",
                statuses=None,
                default_status="backlog",
            )

    def test_statuses_are_unique(self):
        assert len(self.task_list.statuses) == 0
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")
        assert len(self.task_list.statuses) == 3
        self.task_list.add_status("ready")
        self.task_list.add_status("working")
        self.task_list.add_status("done")
        assert len(self.task_list.statuses) == 3

    async def test_can_remove_status_from_list(self):
        self.task_list.add_status("READY")
        await self.task_list.remove_status("READY", TaskRepositoryPlaceholder())

        assert isinstance(self.task_list.statuses, set)
        assert "READY" not in self.task_list.statuses
        assert "READY" not in self.task_list.statuses
