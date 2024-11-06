from ..aggregate import Aggregate
from .errors import ArchivedStatusError, InvalidStatusError
from .ports import TaskDao

# Constants
ARCHIVED_STATUS = "ARCHIVED"


# Aggregate
class TaskList(Aggregate):
    _name: str
    _pk: int | None
    _statuses: set[str]
    _default_status: str | None

    def __init__(
        self,
        *,
        name: str,
        pk: int | None = None,
        statuses: set[str] | None = None,
        default_status: str | None = None,
    ):
        super().__init__()

        self._pk = pk
        self._name = name

        if not statuses:
            statuses = set()

        statuses.add(ARCHIVED_STATUS)
        self._statuses = statuses

        if default_status:
            self.default_status = default_status

    @property
    def pk(self) -> int:
        if self._pk is None:
            msg = "TaskList pk is not set"
            raise ValueError(msg)
        return self._pk

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_status(self) -> str | None:
        return self._default_status

    @default_status.setter
    def default_status(self, status: str) -> None:
        if status not in self.statuses:
            raise InvalidStatusError(status=status)
        self._default_status = status

    @property
    def statuses(self) -> set[str]:
        return self._statuses

    def add_status(self, status: str) -> None:
        self._statuses.add(status)

    async def remove_status(
        self,
        *,
        status: str,
        dao: TaskDao,
        migration_status: str | None = None,
    ) -> None:
        if status == ARCHIVED_STATUS:
            raise ArchivedStatusError  # cannot remove this status

        if status not in self._statuses:
            return

        if migration_status and migration_status not in self._statuses:
            raise InvalidStatusError(status=migration_status)

        # Note we are passing in a repo rather than eager load for scalability concerns
        await dao.update_all_tasks_with_status(
            task_list_pk=self.pk,
            status=status,
            migration_status=migration_status or ARCHIVED_STATUS,
        )

        self._statuses.remove(status)
