import pytest

from app.infra import close_connections, init_connections


@pytest.fixture(autouse=True)
async def connections():  # noqa: PT004, ANN201
    await init_connections()
    yield
    await close_connections(cleanup=True)
