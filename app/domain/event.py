from typing import Any

from pydantic import BaseModel

Payload = dict[str, Any] | str


class Event(BaseModel):
    channel: str
    data: Payload
