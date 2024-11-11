# ruff: noqa: F403

from kink import di, inject

from app.config import config

from .connection import Connection

# Initialize Infra
match config.ENVIRONMENT:
    case "local":
        from .memory.cache import *
        from .memory.publisher import *
        from .sqlalchemy.query import *
        from .sqlalchemy.uow import *
    case _:
        from .memory.cache import *
        from .nats.publisher import *
        from .sqlalchemy.query import *
        from .sqlalchemy.uow import *


@inject()
class InfraInitializer:
    connections: list[Connection]

    def __init__(self, connections: list[Connection]):
        self.connections = connections

    async def init_connections(self) -> None:
        for connection in self.connections:
            await connection.connect()

    async def close_connections(self, *, cleanup: bool = False) -> None:
        for connection in self.connections:
            await connection.close(cleanup=cleanup)


infra_initializer = di[InfraInitializer]


async def init_connections() -> None:
    await infra_initializer.init_connections()


async def close_connections(*, cleanup: bool = False) -> None:
    await infra_initializer.close_connections(cleanup=cleanup)
