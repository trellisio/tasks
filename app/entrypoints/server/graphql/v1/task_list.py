import strawberry
from kink import di

from app.services.task_list import v1


@strawberry.type
class Task:
    pk: int
    title: str
    status: str
    description: str | None
    tags: list[str] | None


@strawberry.type
class Status:
    label: str

    @strawberry.field
    async def tasks(self, info: strawberry.Info) -> list[Task]:
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        return await svc.view_task_list_tasks(list_id=info.context["list_id"], status=self.label, serializer=Task)


@strawberry.type
class TaskList:
    pk: int
    name: str
    default_status: str | None
    statuses: list[Status]

    def __init__(self, *, pk: int, name: str, default_status: str | None, statuses: list[str]):
        self.pk = pk
        self.name = name
        self.default_status = default_status
        self.statuses = [Status(label=status) for status in statuses]


@strawberry.type
class TaskListQuery:
    @strawberry.field
    async def get_names(  # noqa: PLR6301
        self,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> strawberry.scalars.JSON:
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        return await svc.view_task_list_names(skip=skip, limit=limit, serializer=dict)

    @strawberry.field
    async def get(  # noqa: PLR6301, PLR0917
        self,
        list_id: int,
        info: strawberry.Info,
    ) -> TaskList:
        info.context["list_id"] = list_id

        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        return await svc.view_task_list(list_id=list_id, serializer=TaskList)


@strawberry.experimental.pydantic.input(model=v1.dtos.CreateTaskListDto, all_fields=True)
class CreateTaskListDto:
    pass


@strawberry.experimental.pydantic.input(model=v1.dtos.UpdateTaskListDto, all_fields=True)
class UpdateTaskListDto:
    pass


@strawberry.experimental.pydantic.input(model=v1.dtos.AddTaskListStatusDto, all_fields=True)
class AddTaskListStatusDto:
    pass


@strawberry.experimental.pydantic.input(model=v1.dtos.RemoveTaskListStatusDto, all_fields=True)
class RemoveTaskListStatusDto:
    pass


@strawberry.experimental.pydantic.input(model=v1.dtos.CreateTaskDto, all_fields=True)
class CreateTaskDto:
    pass


@strawberry.experimental.pydantic.input(model=v1.dtos.UpdateTaskDto, all_fields=True)
class UpdateTaskDto:
    pass


@strawberry.type
class TaskListMutation:
    @strawberry.field
    async def create(self, create_task_list: CreateTaskListDto) -> int:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        return await svc.create_task_list(create_task_list)

    @strawberry.field
    async def update_info(self, *, task_list_id: int, update_task_info: UpdateTaskListDto) -> TaskList:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        task_list = await svc.update_task_list(task_list_id=task_list_id, update_task_list=update_task_info)
        return TaskList(
            pk=task_list.pk,
            name=task_list.name,
            default_status=task_list.default_status,
            statuses=task_list.statuses,
        )

    @strawberry.field
    async def add_status(self, *, task_list_id: int, status: AddTaskListStatusDto) -> TaskList:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        task_list = await svc.add_task_list_status(task_list_id=task_list_id, status=status)
        return TaskList(
            pk=task_list.pk,
            name=task_list.name,
            default_status=task_list.default_status,
            statuses=task_list.statuses,
        )

    @strawberry.field
    async def remove_status(self, *, task_list_id: int, status: RemoveTaskListStatusDto) -> TaskList:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        task_list = await svc.remove_task_list_status(task_list_id=task_list_id, status=status)
        return TaskList(
            pk=task_list.pk,
            name=task_list.name,
            default_status=task_list.default_status,
            statuses=task_list.statuses,
        )

    @strawberry.field
    async def create_task(self, *, task_list_id: int, create_task: CreateTaskDto) -> Task:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        task = await svc.create_task(task_list_id=task_list_id, create_task=create_task)
        return Task(
            pk=task.pk,
            title=task.title,
            status=task.status,
            description=task.description,
            tags=task.tags,
        )

    @strawberry.field
    async def update_task(self, *, task_id: int, update_task: UpdateTaskDto) -> Task:  # noqa: PLR6301
        svc: v1.TaskListReadService = di[v1.TaskListReadService]
        task = await svc.update_task(task_id=task_id, update_task=update_task)
        return Task(
            pk=task.pk,
            title=task.title,
            status=task.status,
            description=task.description,
            tags=task.tags,
        )
