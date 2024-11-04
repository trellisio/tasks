from abc import ABC, abstractmethod


class Connection(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self, *, cleanup: bool = False) -> None:
        pass
