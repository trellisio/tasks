from .task_list import TaskList
from ..aggregate import Aggregate

class Task(Aggregate):
    _title: str
    _description: str
    _status: str
    _task_list: TaskList
    _tags: set[str]
    
    def __init__(self, *, title: str, description: str, status: str, task_list: TaskList, tags: list[str] | None = None):
        self._title = title
        self._description = description
        self._status = status
        self._task_list = task_list
        
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
        if not new_status in self.task_list.statuses:
            raise ValueError(f"Invalid status {new_status}. Available statuses are: {self.task_list.statuses}")
        
        self.status = new_status
    
    @property
    def task_list(self):
        return self._task_list
    
    @property
    def tags(self):
        return self._tags
