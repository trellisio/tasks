from typing import Type

from kink import inject

from ...errors import NoResourceError
from ...ports import Query, Uow


@inject()
class TaskListReadService:
    query: Query
    uow: Uow

    def __init__(self, *, query: Query, uow: Uow):
        self.query = query
        self.uow = uow

    async def view_task_list_names[T](
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        serializer: Type[T],  # noqa: FA100
    ) -> list[T]:
        return await self.query.execute(
            query="""
                        SELECT "id" AS "pk", "name" FROM "task_list"
                        LIMIT :limit
                        OFFSET :offset
            """,
            params={"limit": limit, "offset": skip},
            serializer=serializer,
        )

    async def view_task_list[T](self, *, list_id: int, serializer: Type[T]) -> T:  # noqa: FA100
        res = await self.query.execute(
            query="""
                    SELECT "id" AS "pk", "name", "statuses", "default_status" FROM "task_list"
                    WHERE "id" = :list_id
                    LIMIT 1
            """,
            params={"list_id": list_id},
            serializer=serializer,
        )
        if not res:
            msg = f"Task list with id {list_id} not found"
            raise NoResourceError(msg=msg)

        return res[0]

    async def view_task_list_tasks[T](
        self,
        *,
        list_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
        serializer: Type[T],  # noqa: FA100
    ) -> list[T]:
        return await self.query.execute(
            query=f"""
                    SELECT "id" AS "pk", "title", "status", "description", "tags" FROM "task"
                    WHERE "task_list_id" = :list_id {"""AND "status" = :status""" if status else ""}
                    LIMIT :limit
                    OFFSET :offset
            """,  # noqa: S608
            params={"list_id": list_id, "status": status, "limit": limit, "offset": skip},
            serializer=serializer,
        )
