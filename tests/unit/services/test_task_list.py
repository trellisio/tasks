import pytest
from kink import di

from app.services.errors import NoResourceError
from app.services.task_list import v1


class TestV1TaskListService:
    service: v1.TaskListWriteService

    @pytest.fixture(autouse=True)
    def set_up(self, connect: None) -> None:  # noqa: PT004, ARG002
        self.service = di[v1.TaskListWriteService]

    async def test_create_task_list(self) -> int:
        dto = v1.dtos.CreateTaskListDto(
            name="dev",
            statuses={"backlog", "ready to work", "working", "validation", "demo ready"},
            default_status="backlog",
        )
        return await self.service.create_task_list(dto)

    async def test_create_task(self) -> None:
        pk = await self.test_create_task_list()
        dto = v1.dtos.CreateTaskDto(title="task 1", status="backlog")
        await self.service.create_task(task_list_id=pk, create_task=dto)

    async def test_error_raised_if_task_list_does_not_exist(self) -> None:
        dto = v1.dtos.CreateTaskDto(title="task 1", status="backlog")
        with pytest.raises(NoResourceError):
            await self.service.create_task(task_list_id=100, create_task=dto)
