from typing import Any, Mapping, Type, cast

from kink import inject
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.ports import Cache, Query

from .connection import SqlConnection


@inject(alias=Query)
class SqlAlchemyQuery(Query):
    session_factory: async_sessionmaker[AsyncSession]
    session: AsyncSession

    def __init__(self, *, connection: SqlConnection, cache: Cache):
        super().__init__(cache=cache)

        self.session_factory = async_sessionmaker(
            connection.read_replica_engine,
            expire_on_commit=False,
        )

    async def execute[T](
        self,
        *,
        query: str,
        params: Mapping[str, Any] | None = None,
        serializer: Type[T],  # noqa: FA100
    ) -> list[T]:
        async with self.session_factory() as session:
            res = await session.execute(
                text(query),
                params,
            )

            rows: list[T] = []
            for row in res.all():
                payload = dict(zip(res.keys(), row))
                if serializer is dict:
                    # if serializer is dict, just ignore
                    rows.append(cast(T, payload))
                else:
                    rows.append(serializer(**payload))

            return rows
