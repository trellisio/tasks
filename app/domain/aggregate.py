from .event import Event


class Aggregate:
    version: int
    _events: list[Event]

    def __init__(self):
        self.version = 0
        self._events = []

    @property
    def events(self) -> list[Event]:
        if not hasattr(self, "_events"):
            self._events = []

        return self._events

    @events.setter
    def events(self):
        raise ValueError("Cannot set events field")

    def emit(self, event: Event):
        self.events.append(event)
