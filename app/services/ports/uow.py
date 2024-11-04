from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from inspect import signature
from typing import TYPE_CHECKING, Any, Literal

from app.domain.aggregate import Aggregate
from app.domain.event import DomainEvent
from app.domain.models import Task, TaskList, ports

from ..reflection import Reflector

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class Repository[T: Aggregate](ABC):
    _seen: set[T]

    def __init__(self):
        self._seen = set()
        self._decorate_methods()

    @property
    def seen(self) -> set[T]:
        return self._seen

    # Internals
    def _decorate_methods(self) -> None:
        self._decorate_method("find")
        self._decorate_method("remove")
        self._decorate_method("add")

    def _get_methods(
        self,
        startswith: Literal["find", "remove", "add"],
    ) -> list[str]:
        return Reflector.get_methods(obj=self, startswith=startswith)

    def _decorate_method(
        self,
        startswith: Literal["find", "remove", "add"],
    ) -> None:
        methods = self._get_methods(startswith)

        decoration = self._add_decorator if startswith == "add" else self._add_to_seen_decorator

        for method in methods:
            decorated_method = decoration(getattr(self, method))
            setattr(self, method, decorated_method)

    def _add_to_seen_decorator(
        self,
        method: Callable[[Any, Any], Awaitable[list[T]]],
    ) -> Callable[[Any, Any], Awaitable[list[T]]]:
        # takes find_* method and adds returned objects to seen set
        @wraps(method)
        async def fn(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            model = await method(*args, **kwargs)
            if isinstance(model, list):
                for m in model:
                    self._seen.add(m)
            else:
                self._seen.add(model)

            return model

        return fn

    def _add_decorator(
        self,
        method: Callable[[Any, Any], Awaitable[list[T]]],
    ) -> Callable[[Any, Any], Awaitable[list[T]]]:
        @wraps(method)
        async def fn(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            # inspect passed method and find param name mapping to T
            sig = signature(method, eval_str=True)
            parameters = sig.parameters
            keys = list(parameters.keys())

            for i in range(len(keys)):
                key = keys[i]
                param_metadata = parameters[key]
                annotation = param_metadata.annotation
                if issubclass(annotation, Aggregate):
                    # Found parameter with annotation to model
                    model = kwargs[key] if key in kwargs else args[i]

                    if isinstance(model, list):
                        self.seen.update(model)
                    else:
                        self.seen.add(model)

            return await method(*args, **kwargs)

        return fn

    @abstractmethod
    async def add(self, agg: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find(self, pk: int) -> list[T]:
        raise NotImplementedError

    # @abstractmethod
    # async def remove(self, agg: T) -> None:
    #     raise NotImplementedError


class TaskListRepository(Repository[TaskList], ABC):
    @abstractmethod
    async def add_tasks(self, tasks: list[Task]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(self, name: str) -> list[TaskList]:
        raise NotImplementedError


class Uow(ABC):
    # repositories
    task_list_repository: TaskListRepository

    # domain DAOs
    task_dao: ports.TaskDao

    # Internals
    _isolation_level: Literal["REPEATABLE READ", "READ COMMITTED"]

    def __init__(self):
        self._decorate_defined_commit_method()
        self._isolation_level = "READ COMMITTED"

    @property
    def repositories(self) -> list[Repository]:
        return [self.task_list_repository]

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc, tb):  # noqa: ANN001, PLR0917
        await self.rollback()
        await self.close()

    def begin(
        self,
        isolation_level: Literal["REPEATABLE READ", "READ COMMITTED"] = "READ COMMITTED",
    ) -> Uow:
        self._isolation_level = isolation_level
        return self

    # Internals

    def _collect_seen_aggregates(self, *, clear: bool = False) -> list[Aggregate]:
        aggs: list[Aggregate] = []
        for repo in self.repositories:
            aggs.extend(repo.seen)
            if clear:
                repo._seen = set()  # noqa: SLF001

        return aggs

    def _collect_events(self) -> list[DomainEvent]:
        events: list[DomainEvent] = []
        seen_aggs = self._collect_seen_aggregates()
        for agg in seen_aggs:
            events.extend(agg.events)
            agg._events = []  # noqa: SLF001

        return events

    def _decorate_defined_commit_method(self) -> None:
        # decorate commit method to auto emit raised domain events
        commit = self.commit

        @wraps(commit)
        async def fn(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            seen_aggs = self._collect_seen_aggregates(clear=True)
            for agg in seen_aggs:
                agg.version += 1

            await commit(*args, **kwargs)

        self.commit = fn  # type: ignore[assignment]
