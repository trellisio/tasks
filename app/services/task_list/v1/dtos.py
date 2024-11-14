from typing import Annotated

from pydantic import BaseModel, Field

StatusFieldRequired = Annotated[str, Field(min_length=1, max_length=50)]
StatusFieldOptional = Annotated[str | None, Field(min_length=1, max_length=50)]


# Input DTOs
class CreateTaskListDto(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    statuses: set[str] | None = None
    default_status: StatusFieldOptional = None


class UpdateTaskListDto(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    default_status: StatusFieldOptional = None


class AddTaskListStatusDto(BaseModel):
    status: StatusFieldRequired


class RemoveTaskListStatusDto(BaseModel):
    status: StatusFieldRequired
    migration_status: StatusFieldOptional = None


class CreateTaskDto(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    status: StatusFieldOptional = None
    description: Annotated[str | None, Field(min_length=1)] = None
    tags: list[str] | None = None


class UpdateTaskDto(BaseModel):
    title: Annotated[str | None, Field(min_length=1)] = None
    status: StatusFieldOptional = None
    description: Annotated[str | None, Field(min_length=1)] = None
    tags: list[str] | None = None


# Output DTOs
class TaskListOutputDto(BaseModel):
    pk: int
    name: str
    statuses: set[str]
    default_status: str | None = None


class TaskOutputDto(BaseModel):
    pk: int
    title: str
    status: str
    description: str | None = None
    tags: set[str] | None = None
