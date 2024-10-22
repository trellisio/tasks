from ..aggregate import Aggregate
from .errors import InvalidStatus
from .task_list import TaskList


class Task(Aggregate):
    _title: str
    _description: str
    _status: str
    _task_list: TaskList
    _tags: set[str]

    def __init__(
        self,
        *,
        title: str,
        description: str,
        status: str,
        task_list: TaskList,
        tags: set[str] | None = None,
    ):
        self._title = title
        self._description = description
        self._task_list = task_list

        self.status = status

        if not tags:
            tags = set()
        self._tags = tags

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status: str):
        if new_status not in self.task_list.statuses:
            raise InvalidStatus(status=new_status)

        self._status = new_status

    @property
    def task_list(self):
        return self._task_list

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag: str):
        self._tags.add(tag)

    def remove_tag(self, tag: str):
        self._tags.remove(tag)
