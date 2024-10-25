import pytest

from app.infra.memory.publisher import InMemoryEventPublisher


class TestInMemoryPublisher:
    publisher: InMemoryEventPublisher

    @pytest.fixture(autouse=True)
    def _set_up(self) -> None:
        self.publisher = InMemoryEventPublisher()

    async def test_can_publish_string_event(self) -> None:
        await self.publisher.publish(channel="event", payload="test")

        assert len(self.publisher.published_messages) == 1
        assert self.publisher.published_messages[0] == {
            "channel": "event",
            "payload": "test",
        }

    async def test_can_publish_dict_event(self) -> None:
        payload = {"subject": "event", "field": "bar"}
        await self.publisher.publish(channel="event", payload=payload)

        assert len(self.publisher.published_messages) == 1
        assert self.publisher.published_messages[0] == {
            "channel": "event",
            "payload": payload,
        }
