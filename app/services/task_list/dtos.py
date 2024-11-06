from pydantic import BaseModel


class CreateTaskListDto(BaseModel):
    name: str
    statuses: set[str] | None = None
    default_status: str | None = None


class CreateTaskDto(BaseModel):
    title: str
    status: str | None = None
    description: str | None = None
    tags: list[str] | None = None
