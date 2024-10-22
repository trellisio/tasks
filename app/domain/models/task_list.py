from typing import Protocol
from ..aggregate import Aggregate

class TaskRepository(Protocol):
    async def update_all_task_statuses_in_list(self, list_id: int, old_status: str, new_status: str):
        ...
        
    async def delete_all_tasks_with_status_in_list(self, list_id: int, status: str):
        ...
    
class TaskList(Aggregate):
    _identifier: int
    _name: str
    _statuses: set[str]
    
    def __init__(self, *, identifier: int, name: str, statuses: set[str] | None = None):
        self._identifier = identifier
        self._name = name
        
        if not statuses:
            statuses = set()
        self._statuses = statuses
    
    @property
    def identifier(self):
        return self._identifier
    
    @property
    def name(self):
        return self._name
    
    @property
    def statuses(self):
        return self._statuses
    
    def add_status(self, status: str):
        self._statuses.add(status)
    
    async def remove_status(self, status: str, task_repo: TaskRepository, migration_status: str | None = None):
        # Note we are passing in a repo rather than eager load for scalability concerns
        if status not in self._statuses:
            return
        
        # on deleting a status, if migration_status is passed, we update task's statuses
        if migration_status:
            await task_repo.update_all_tasks_with_status(self._identifier, status, migration_status)
        else:
            # if not passed, delete tasks with this status
            await task_repo.delete_all_tasks_with_status(self._identifier, status)

        self._statuses.remove(status)
