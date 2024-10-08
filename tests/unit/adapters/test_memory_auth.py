import pytest

from app.infra.memory.auth import InMemoryAuth


class TestInMemoryAuth:
    auth: InMemoryAuth

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.cache = InMemoryAuth()
