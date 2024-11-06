from typing import Any, AsyncGenerator

import pytest

from app.infra import close_connections, init_connections


@pytest.fixture(scope="session")
async def connect() -> AsyncGenerator[Any, None]:  # noqa: PT004
    await init_connections()
    yield
    await close_connections(cleanup=True)
