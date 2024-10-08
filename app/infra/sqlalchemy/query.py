from kink import inject
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.ports import Cache, Query

from .connection import SqlConnection


@inject(alias=Query)
class SqlAlchemyQuery(Query):
    session_factory: async_sessionmaker[AsyncSession]
    session: AsyncSession

    def __init__(self, connection: SqlConnection, cache: Cache):
        super().__init__(cache)

        self.session_factory = async_sessionmaker(
            connection.default_engine,
            expire_on_commit=False,
        )

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[str]:
        async with self.session_factory() as session:
            res = await session.execute(
                text(f"""
                    SELECT "email" FROM "user"
                    LIMIT {limit}
                    OFFSET {skip}
                """)
            )
            return [r[0] for r in res]
