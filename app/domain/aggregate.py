from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

    def emit(self, event: Event) -> None:
        self.events.append(event)
