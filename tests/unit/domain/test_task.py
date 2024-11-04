import pytest

from app.domain.models import Task, TaskList
from app.domain.models.errors import InvalidStatusError


class TestTask:
    task_list: TaskList
    task: Task

    @pytest.fixture(autouse=True)
    def _set_up(self) -> None:
        task_list = TaskList(
            name="todo",
            statuses={"ready", "working", "done"},
        )
        self.task = Task(
            title="Finish Feature",
            description="Random text describing the task to be completed",
            task_list=task_list,
            status="ready",
            tags={"example"},
        )

    def test_can_add_tag(self) -> None:
        self.task.add_tag("test")
        assert "test" in self.task.tags

    def test_can_remove_tag(self) -> None:
        self.task.add_tag("test")
        self.task.remove_tag("test")
        assert "test" not in self.task.tags

    def test_error_raised_if_status_not_in_task_list(self) -> None:
        with pytest.raises(InvalidStatusError):
            Task(
                title="Finish Feature",
                description="Random text describing the task to be completed",
                task_list=self.task.task_list,
                status="backlog",
                tags={"example"},
            )

    def test_error_raised_when_task_list_set(self) -> None:
        with pytest.raises(AttributeError):
            self.task.task_list = TaskList(name="todo2", statuses=set())  # type: ignore[misc]
