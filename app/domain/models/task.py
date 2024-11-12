from ..aggregate import Aggregate
from .errors import InvalidStatusError
from .task_list import TaskList


class Task(Aggregate):
    _title: str
    _pk: int | None
    _status: str
    _description: str | None
    _tags: set[str]

    # task_list
    _task_list: TaskList

    def __init__(
        self,
        *,
        title: str,
        task_list: TaskList,
        status: str | None = None,
        pk: int | None = None,
        description: str | None = None,
        tags: set[str] | None = None,
    ):
        self._title = title
        self._pk = pk
        self._description = description
        self._task_list = task_list

        status = status or task_list.default_status
        if status is None:
            raise InvalidStatusError(status="None")
        self.status = status

        if not tags:
            tags = set()
        self._tags = tags

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new_title: str) -> None:
        self._title = new_title

    @property
    def pk(self) -> int:
        if self._pk is None:
            msg = "Task pk is not set"
            raise ValueError(msg)
        return self._pk

    @property
    def description(self) -> str | None:
        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        self._description = new_description

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        if new_status not in self.task_list.statuses:
            raise InvalidStatusError(status=new_status)

        self._status = new_status

    @property
    def task_list(self) -> TaskList:
        return self._task_list

    @property
    def tags(self) -> set[str]:
        if isinstance(self._tags, list):
            self._tags = set(self._tags)

        return self._tags

    def add_tag(self, tag: str) -> None:
        self._tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        self._tags.remove(tag)
