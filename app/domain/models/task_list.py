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
    _user_id: str

    def __init__(
        self,
        *,
        name: str,
        user_id: str,
        pk: int | None = None,
        statuses: set[str] | None = None,
        default_status: str | None = None,
    ):
        super().__init__()

        self._name = name
        self._user_id = user_id
        self._pk = pk

        if not statuses:
            statuses = set()

        statuses.add(ARCHIVED_STATUS)
        self._statuses = statuses

        self.default_status = default_status

    @property
    def pk(self) -> int:
        if self._pk is None:
            msg = "TaskList pk is not set"
            raise ValueError(msg)
        return self._pk

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def default_status(self) -> str | None:
        return self._default_status

    @default_status.setter
    def default_status(self, status: str | None) -> None:
        if status is not None and status not in self.statuses:
            raise InvalidStatusError(status=status)
        self._default_status = status

    @property
    def statuses(self) -> set[str]:
        # Bad solution to quickly deal with DB
        if isinstance(self._statuses, list):
            self._statuses = set(self._statuses)

        return self._statuses

    def add_status(self, status: str) -> None:
        if not status:
            raise InvalidStatusError(status=status)
        self.statuses.add(status)

    async def remove_status(
        self,
        *,
        status: str,
        dao: TaskDao,
        migration_status: str | None = None,
    ) -> None:
        if status == ARCHIVED_STATUS:
            raise ArchivedStatusError  # cannot remove this status

        if status not in self.statuses:
            return

        if migration_status and migration_status not in self.statuses:
            raise InvalidStatusError(status=migration_status)

        # Note we are passing in a repo rather than eager load for scalability concerns
        await dao.update_all_tasks_with_status(
            task_list_pk=self.pk,
            status=status,
            migration_status=migration_status or ARCHIVED_STATUS,
        )

        self.statuses.remove(status)
