from typing import TypedDict

from classy_fastapi import Routable, get, post
from kink import di, inject

from app.services.ports.query import Result
from app.services.task_list import v1


class CreatedResourceDto(TypedDict):
    pk: int


@inject()
class TaskListV1Routes(Routable):
    write_service: v1.TaskListWriteService
    read_service: v1.TaskListReadService

    def __init__(self, *, write_service: v1.TaskListWriteService, read_service: v1.TaskListReadService):
        super().__init__()
        self.write_service = write_service
        self.read_service = read_service

    @get("/")
    async def get_task_list_names(self) -> Result:
        return await self.read_service.view_task_list_names()

    @post("/", status_code=201)
    async def create_task_list(self, create_task_list: v1.dtos.CreateTaskListDto) -> CreatedResourceDto:
        pk = await self.write_service.create_task_list(create_task_list)
        return {"pk": pk}

    @get("/{list_id}")
    async def get_task_list(self, list_id: int) -> Result:
        return await self.read_service.view_task_list(list_id)

    @post("/{list_id}/tasks", status_code=201)
    async def create_task(self, *, list_id: int, create_task: v1.dtos.CreateTaskDto) -> CreatedResourceDto:
        pk = await self.write_service.create_task(task_list_id=list_id, create_task=create_task)
        return {"pk": pk}


task_list_v1_routes = di[TaskListV1Routes]
