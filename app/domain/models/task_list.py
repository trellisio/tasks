from __future__ import annotations

from typing import Protocol

from ..aggregate import Aggregate
from .errors import InvalidStatusError


# Interfaces
class TaskRepository(Protocol):
    async def update_all_tasks_with_status(
        self,
        *,
        list_id: int,
        old_status: str,
        new_status: str,
    ) -> None: ...

    async def delete_all_tasks_with_status(self, *, list_id: int, status: str) -> None: ...


# Aggregate
class TaskList(Aggregate):
    _identifier: int
    _name: str
    _statuses: set[str]
    _default_status: str

    def __init__(
        self,
        *,
        identifier: int,
        name: str,
        statuses: set[str] | None = None,
        default_status: str | None = None,
    ):
        self._identifier = identifier
        self._name = name

        if not statuses:
            statuses = set()
        self._statuses = statuses

        if default_status:
            self.default_status = default_status

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_status(self) -> str:
        return self._default_status

    @default_status.setter
    def default_status(self, status: str) -> None:
        if status not in self.statuses:
            raise InvalidStatusError(status=status)
        self._default_status = status

    @property
    def statuses(self) -> set[str]:
        if self._statuses is None:
            self._statuses = set()

        return self._statuses

    def add_status(self, status: str) -> None:
        self._statuses.add(status)

    async def remove_status(
        self,
        *,
        status: str,
        task_repo: TaskRepository,
        migration_status: str | None = None,
    ) -> None:
        # Note we are passing in a repo rather than eager load for scalability concerns
        if status not in self._statuses:
            return

        # on deleting a status, if migration_status is passed, we update task's statuses
        if migration_status:
            await task_repo.update_all_tasks_with_status(
                list_id=self._identifier,
                old_status=status,
                new_status=migration_status,
            )
        else:
            # if not passed, delete tasks with this status
            await task_repo.delete_all_tasks_with_status(
                list_id=self._identifier,
                status=status,
            )

        self._statuses.remove(status)
