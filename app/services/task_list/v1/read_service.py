from kink import inject

from ...ports import Query, Uow
from ...ports.query import Result


@inject()
class TaskListReadService:
    query: Query
    uow: Uow

    def __init__(self, *, query: Query, uow: Uow):
        self.query = query
        self.uow = uow

    async def view_task_list_names(self, *, skip: int = 0, limit: int = 50) -> Result:
        return await self.query.execute(
            query="""
                        SELECT "id" AS "pk", "name" FROM "task_list"
                        LIMIT :limit
                        OFFSET :offset
            """,
            params={"limit": limit, "offset": skip},
        )

    async def view_task_list(self, list_id: int) -> Result:
        return await self.query.execute(
            query="""
                    SELECT "id" AS "pk", "name", "statuses", "default_status" FROM "task_list"
                    WHERE "id" = :list_id
                    LIMIT 1
            """,
            params={"list_id": list_id},
        )

    async def view_task_list_tasks(
        self,
        *,
        list_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Result:
        return await self.query.execute(
            query=f"""
                    SELECT "id" AS "pk", "title", "status", "description", "tags" FROM "task"
                    WHERE "task_list_id" = :list_id {"""AND "status" = :status""" if status else ""}
                    LIMIT :limit
                    OFFSET :offset
            """,  # noqa: S608
            params={"list_id": list_id, "status": status, "limit": limit, "offset": skip},
        )
