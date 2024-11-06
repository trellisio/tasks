from typing import TypedDict

from classy_fastapi import Routable, post
from kink import di, inject

from app.services.task_list import dtos
from app.services.task_list.service import TaskListWriteService


class CreatedResourceDto(TypedDict):
    pk: int


@inject()
class TaskListRoutes(Routable):
    write_service: TaskListWriteService

    def __init__(self, write_service: TaskListWriteService):
        super().__init__()
        self.write_service = write_service

    @post("/", status_code=201)
    async def create_task_list(self, create_task_list: dtos.CreateTaskListDto) -> CreatedResourceDto:
        pk = await self.write_service.create_task_list(create_task_list)
        return {"pk": pk}

    @post("/{list_id}/tasks", status_code=201)
    async def create_task(self, *, list_id: int, create_task: dtos.CreateTaskDto) -> CreatedResourceDto:
        pk = await self.write_service.create_task(task_list_id=list_id, create_task=create_task)
        return {"pk": pk}


task_list_routes = di[TaskListRoutes]
