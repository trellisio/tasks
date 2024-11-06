from .event import DomainEvent


class Aggregate:
    _version: int
    _events: list[DomainEvent]

    def __init__(self):
        self._version = 0
        self._events = []

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, version: int) -> None:
        self._version = version

    @property
    def events(self) -> list[DomainEvent]:
        if not hasattr(self, "_events"):
            self._events = []

        return self._events

    def emit(self, event: DomainEvent) -> None:
        self.events.append(event)
