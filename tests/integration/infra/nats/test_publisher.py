import pytest

from app.infra.nats.publisher import NatsConnection, NatsEventPublisher


class TestNatsPublisher:
    publisher: NatsEventPublisher

    @pytest.fixture(autouse=True)
    async def set_up(self):
        connection = NatsConnection()
        await connection.connect()
        self.publisher = NatsEventPublisher(connection)

    async def test_can_publish_string_event(self):
        await self.publisher.publish("event", "test")

    async def test_can_publish_dict_event(self):
        payload = {"subject": "event", "field": "bar"}
        await self.publisher.publish("event", payload)
