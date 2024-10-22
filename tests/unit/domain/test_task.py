import pytest

from app.domain.models import Task, TaskList
from app.domain.models.errors import InvalidStatus


class TestTask:
    task_list: TaskList
    task: Task

    @pytest.fixture(autouse=True)
    def set_up(self):
        task_list = TaskList(
            identifier=1, name="todo", statuses={"ready", "working", "done"}
        )
        self.task = Task(
            title="Finish Feature",
            description="Random text describing the task to be completed",
            task_list=task_list,
            status="ready",
            tags={"example"},
        )

    def test_can_add_tag(self):
        self.task.add_tag("test")
        assert "test" in self.task.tags

    def test_can_remove_tag(self):
        self.task.add_tag("test")
        self.task.remove_tag("test")
        assert "test" not in self.task.tags

    def test_error_raised_if_status_not_in_task_list(self):
        with pytest.raises(InvalidStatus):
            Task(
                title="Finish Feature",
                description="Random text describing the task to be completed",
                task_list=self.task.task_list,
                status="backlog",
                tags={"example"},
            )

    def test_error_raised_when_task_list_set(self):
        with pytest.raises(AttributeError):
            self.task.task_list = TaskList(identifier=2, name="todo2", statuses={})
