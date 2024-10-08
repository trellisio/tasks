from abc import ABC, abstractmethod


class Connection(ABC):
    @abstractmethod
    async def connect():
        pass

    @abstractmethod
    async def close(self, cleanup: bool = False):
        pass
