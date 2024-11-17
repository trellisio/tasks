import strawberry

from .task_list import TaskListMutation, TaskListQuery


@strawberry.type
class V1Query:
    task_list: TaskListQuery = strawberry.field(resolver=TaskListQuery, description="Task List service")


@strawberry.type
class V1Mutation:
    task_list: TaskListMutation = strawberry.field(resolver=TaskListMutation, description="Task List service")
