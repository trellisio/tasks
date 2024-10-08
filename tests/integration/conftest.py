import pytest

from app.infra import close_connections, init_connections


@pytest.fixture()
async def connections():
    await init_connections()
    yield
    await close_connections(cleanup=True)
