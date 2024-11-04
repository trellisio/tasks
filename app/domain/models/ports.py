from __future__ import annotations

from typing import Protocol


class TaskDao(Protocol):
    """An abstraction to deal with tasks at bulk, without having to eager load on the aggregate"""

    async def update_all_tasks_with_status(
        self,
        *,
        task_list_pk: int,
        status: str,
        migration_status: str,
    ) -> None: ...
