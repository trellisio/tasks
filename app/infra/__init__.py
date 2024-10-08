# ruff: noqa: F403
from kink import di, inject

from app.config import config

from .connection import Connection

# Initialize Infra
match config.ENVIRONMENT:
    case "local":
        from .memory.auth import *
        from .memory.cache import *  # noqa: F403
        from .memory.metrics import *
        from .memory.publisher import *
        from .sqlalchemy.query import *
        from .sqlalchemy.uow import *
    case _:
        from .keycloak.auth import *
        from .nats.publisher import *
        from .prometheus.metrics import *
        from .redis.cache import *
        from .sqlalchemy.query import *
        from .sqlalchemy.uow import *


@inject()
class InfraInitializer:
    connections: list[Connection]

    def __init__(self, connections: list[Connection]):
        self.connections = connections

    async def init_connections(self):
        for connection in self.connections:
            await connection.connect()

    async def close_connections(self, cleanup: bool = False):
        for connection in self.connections:
            await connection.close(cleanup)


infra_initializer = di[InfraInitializer]


async def init_connections():
    await infra_initializer.init_connections()


async def close_connections(cleanup: bool = False):
    await infra_initializer.close_connections(cleanup)
