from kink import inject

from app.domain.models import Task, TaskList
from app.logger import logger

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
            statuses=list(create_task_list.statuses) if create_task_list.statuses else None,
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
            logger.info(f"Removed status {status.status} from task list {task_list_id}. Tasks updated.")

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
                logger.error(f"Task list {task_list_id} does not exist")
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

    async def update_task(self, *, task_id: int, update_task: dtos.UpdateTaskDto) -> dtos.TaskOutputDto:
        async with self.uow:
            task = await self.uow.task_dao.get_task(task_id)
            if not task:
                logger.error(f"Task {task_id} does not exist")
                raise errors.NoResourceError(msg=f"Task {task_id} does not exist")

            task.title = update_task.title or task.title
            task.status = update_task.status or task.status
            task.description = update_task.description or task.description
            if update_task.tags:
                for tag in update_task.tags:
                    task.add_tag(tag)

            await self.uow.commit()

            return dtos.TaskOutputDto(
                pk=task.pk,
                title=task.title,
                status=task.status,
                description=task.description,
                tags=task.tags,
            )

    # Utils
    async def _get_task_list(self, task_list_id: int) -> TaskList:
        task_lists = await self.uow.task_list_repository.find(task_list_id)
        if not task_lists:
            logger.error(f"Task list {task_list_id} does not exist")
            raise errors.NoResourceError(msg=f"Task list {task_list_id} does not exist")
        if len(task_lists) > 1:
            logger.error(f"Found multiple task lists with id {task_list_id}")
            raise errors.ServiceError(msg=f"Found multiple task lists with id {task_list_id}")

        return task_lists[0]
