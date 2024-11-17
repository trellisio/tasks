from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings
from strawberry.fastapi import GraphQLRouter

from app.infra import close_connections, init_connections
from app.logger import logger

from .schema import schema


class GraphqlConfig(BaseSettings):
    FASTAPI_ENV: str = Field(
        description="Environment server is running in",
        default="development",
    )
    PORT: int = Field(description="Port for server", default=8000)
    URL_PREFIX: str = Field(description="URL to prefix routes on server", default="")


config = GraphqlConfig()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_connections()
    logger.info("Connections initialized 🚀")

    graphql_router: GraphQLRouter = GraphQLRouter(
        schema,
        graphql_ide="graphiql" if config.FASTAPI_ENV == "development" else None,
    )
    app.include_router(graphql_router, prefix="/graphql")
    logger.info("Server started 🚀")

    yield

    # cleanup on shutdown
    await close_connections()


app = FastAPI(lifespan=lifespan)


def listen() -> None:
    uvicorn.run(
        "app.entrypoints.server.graphql:app",
        host="0.0.0.0",  # noqa: S104
        port=config.PORT,
        reload=config.FASTAPI_ENV == "development",
        proxy_headers=True,
    )
