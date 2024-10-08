from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from functools import wraps
from inspect import signature
from typing import Any, Literal

from app.domain.aggregate import Aggregate
from app.domain.event import Event
from app.domain.models import User

from ..reflection import Reflector
from .publisher import Publisher


class Repository[T: Aggregate](ABC):
    _seen: set[T]

    def __init__(self):
        self._seen = set()
        self._decorate_methods()

    @property
    def seen(self) -> set[T]:
        return self._seen

    @seen.setter
    def seen(self, _: Any):
        raise ValueError("Seen cannot be set")

    # Internals
    def _decorate_methods(self):
        self._decorate_method("find")
        self._decorate_method("remove")
        self._decorate_method("add")

    def _get_methods(
        self, startswith: Literal["find"] | Literal["remove"] | Literal["add"]
    ) -> list[str]:
        return Reflector._get_methods(self, startswith)

    def _decorate_method(
        self, startswith: Literal["find"] | Literal["remove"] | Literal["add"]
    ):
        methods = self._get_methods(startswith)

        if startswith == "add":
            decoration = self._add_decorator
        else:
            decoration = self._add_to_seen_decorator

        for method in methods:
            decorated_method = decoration(getattr(self, method))
            setattr(self, method, decorated_method)

    def _add_to_seen_decorator(
        self, method: Callable[[Any, Any], Awaitable[list[T]]]
    ) -> Callable[[Any, Any], Awaitable[list[T]]]:
        # takes find_* method and adds returned objects to seen set
        @wraps(method)
        async def fn(*args, **kwargs):
            model = await method(*args, **kwargs)
            if isinstance(model, list):
                for m in model:
                    self._seen.add(m)
            else:
                self._seen.add(model)

            return model

        return fn

    def _add_decorator(
        self, method: Callable[[Any, Any], Awaitable[list[T]]]
    ) -> Callable[[Any, Any], Awaitable[list[T]]]:
        @wraps(method)
        async def fn(*args, **kwargs):
            # inspect passed method and find param name mapping to T
            sig = signature(method)
            parameters = sig.parameters
            keys = list(parameters.keys())

            for i in range(len(keys)):
                key = keys[i]
                param_metadata = parameters[key]
                annotation = param_metadata.annotation

                if issubclass(annotation, Aggregate):
                    # Found parameter with annotation to model
                    if key in kwargs:
                        model = kwargs[key]
                    else:
                        model = args[i]

                    if isinstance(model, list):
                        self.seen.update(model)
                    else:
                        self.seen.add(model)

            return await method(*args, **kwargs)

        return fn

    @abstractmethod
    async def add(self):
        raise NotImplementedError()

    @abstractmethod
    async def find(self) -> list[T]:
        raise NotImplementedError()

    @abstractmethod
    async def remove(self) -> list[T]:
        raise NotImplementedError()


class UserRepository(Repository[User], ABC):
    @abstractmethod
    async def add(self, user: User):
        raise NotImplementedError()

    @abstractmethod
    async def find(self, email: str) -> list[User]:
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, email: str) -> list[User]:
        raise NotImplementedError()


class Uow(ABC):
    # repositories
    user_repository: UserRepository

    # Internals
    _publisher: Publisher
    _isolation_level: Literal["REPEATABLE READ"] | Literal["READ COMMITTED"]

    def __init__(self, publisher: Publisher):
        self._publisher = publisher
        self._decorate_defined_commit_method()
        self._isolation_level = "READ COMMITTED"

    @property
    def repositories(self) -> list[Repository]:
        return [self.user_repository]

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError()

    @abstractmethod
    async def close(self):
        raise NotImplementedError()

    async def __aexit__(self, exc_type, exc, tb):
        await self.rollback()
        await self.close()

    def begin(
        self,
        isolation_level: Literal["REPEATABLE READ"]
        | Literal["READ COMMITTED"] = "READ COMMITTED",
    ):
        self._isolation_level = isolation_level
        return self

    # Internals

    def _collect_seen_aggregates(self, clear: bool = False) -> list[Aggregate]:
        aggs: list[Aggregate] = []
        for repo in self.repositories:
            aggs.extend(repo.seen)
            if clear:
                repo._seen = set()

        return aggs

    def _collect_events(self) -> list[Event]:
        events: list[Event] = []
        seen_aggs = self._collect_seen_aggregates()
        for agg in seen_aggs:
            events.extend(agg.events)
            agg._events = []

        return events

    def _decorate_defined_commit_method(self):
        # decorate commit method to auto emit raised domain events
        commit = getattr(self, "commit")

        @wraps(commit)
        async def fn(*args, **kwargs):
            domain_events = self._collect_events()
            for event in domain_events:
                await self._publisher.publish(event.channel, event.data)

            seen_aggs = self._collect_seen_aggregates(clear=True)
            for agg in seen_aggs:
                agg.version += 1

            await commit(*args, **kwargs)

        setattr(self, "commit", fn)
