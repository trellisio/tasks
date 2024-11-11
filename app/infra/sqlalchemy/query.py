from typing import Any, Mapping

from kink import inject
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.ports import Cache, Query
from app.services.ports.query import Result

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

    async def execute(self, *, query: str, params: Mapping[str, Any] | None = None) -> Result:
        async with self.session_factory() as session:
            res = await session.execute(
                text(query),
                params,
            )

            rows = []
            for row in res.all():
                payload = {}
                for i, key in enumerate(res.keys()):
                    payload[key] = row[i]
                rows.append(payload)

            return rows
