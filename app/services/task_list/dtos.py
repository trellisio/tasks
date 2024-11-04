from __future__ import annotations

from pydantic import BaseModel


class CreateTaskListDto(BaseModel):
    name: str
    statuses: set[str] | None = None
    default_status: str | None = None


class CreateTaskDto(BaseModel):
    title: str
    status: str
    task_list_id: int
    description: str | None
    tags: list[str] | None
