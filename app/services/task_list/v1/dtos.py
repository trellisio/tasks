from pydantic import BaseModel


# Input DTOs
class CreateTaskListDto(BaseModel):
    name: str
    statuses: set[str] | None = None
    default_status: str | None = None


class UpdateTaskListDto(BaseModel):
    name: str | None = None
    default_status: str | None = None


class AddTaskListStatusDto(BaseModel):
    status: str


class RemoveTaskListStatusDto(BaseModel):
    status: str
    migration_status: str | None = None


class CreateTaskDto(BaseModel):
    title: str
    status: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class UpdateTaskDto(BaseModel):
    title: str | None = None
    status: str | None = None
    description: str | None = None
    tags: list[str] | None = None


# Output DTOs


class TaskListOutputDto(BaseModel):
    pk: int
    name: str
    statuses: set[str]
    default_status: str | None


class TaskOutputDto(BaseModel):
    pk: int
    title: str
    status: str
    description: str | None
    tags: set[str] | None
