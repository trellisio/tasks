from kink import inject

from app.domain.models import Task, TaskList

from ... import errors
from ...ports import Uow
from . import dtos


@inject()
class TaskListWriteService:
    uow: Uow

    def __init__(self, uow: Uow):
        self.uow = uow

    async def create_task_list(self, create_task_list: dtos.CreateTaskListDto) -> int:
        task_list = TaskList(
            name=create_task_list.name,
            statuses=create_task_list.statuses,
            default_status=create_task_list.default_status,
        )

        async with self.uow:
            await self.uow.task_list_repository.add(task_list)
            await self.uow.commit()

        return task_list.pk

    async def update_task_list(
        self,
        *,
        task_list_id: int,
        update_task_list: dtos.UpdateTaskListDto,
    ) -> dtos.TaskListOutputDto:
        async with self.uow:
            task_list = await self._get_task_list(task_list_id)
            task_list.name = update_task_list.name or task_list.name
            task_list.default_status = update_task_list.default_status or task_list.default_status

            await self.uow.commit()

            return dtos.TaskListOutputDto(
                pk=task_list.pk,
                name=task_list.name,
                statuses=task_list.statuses,
                default_status=task_list.default_status,
            )

    async def add_task_list_status(
        self,
        *,
        task_list_id: int,
        status: dtos.AddTaskListStatusDto,
    ) -> dtos.TaskListOutputDto:
        async with self.uow:
            task_list = await self._get_task_list(task_list_id)
            task_list.add_status(status.status)

            await self.uow.commit()

            return dtos.TaskListOutputDto(
                pk=task_list.pk,
                name=task_list.name,
                statuses=task_list.statuses,
                default_status=task_list.default_status,
            )

    async def remove_task_list_status(
        self,
        *,
        task_list_id: int,
        status: dtos.RemoveTaskListStatusDto,
    ) -> dtos.TaskListOutputDto:
        async with self.uow:
            task_list = await self._get_task_list(task_list_id)
            await task_list.remove_status(status=status.status, dao=self.uow.task_dao)

            await self.uow.commit()

            return dtos.TaskListOutputDto(
                pk=task_list.pk,
                name=task_list.name,
                statuses=task_list.statuses,
                default_status=task_list.default_status,
            )

    async def create_task(self, *, task_list_id: int, create_task: dtos.CreateTaskDto) -> int:
        async with self.uow:
            task_list = await self.uow.task_list_repository.find(task_list_id)
            if not task_list:
                raise errors.NoResourceError(msg=f"Task list {task_list_id} does not exist")

            task = Task(
                title=create_task.title,
                status=create_task.status,
                task_list=task_list[0],
                description=create_task.description,
                tags=set(create_task.tags) if create_task.tags else None,
            )
            await self.uow.task_list_repository.add_tasks([task])
            await self.uow.commit()

            return task.pk

    # Utils
    async def _get_task_list(self, task_list_id: int) -> TaskList:
        task_lists = await self.uow.task_list_repository.find(task_list_id)
        if not task_lists:
            raise errors.NoResourceError(msg=f"Task list {task_list_id} does not exist")
        if len(task_lists) > 1:
            raise errors.ServiceError(msg=f"Found multiple task lists with id {task_list_id}")

        return task_lists[0]
