from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings

from app.infra import close_connections, init_connections
from app.logger import logger

from .handlers import register_handlers
from .middlewares import register_middlewares


class FastApiConfig(BaseSettings):
    FASTAPI_ENV: str = Field(
        description="Environment server is running in",
        default="development",
    )
    PORT: int = Field(description="Port for server", default=8000)
    URL_PREFIX: str = Field(description="URL to prefix routes on server", default="")


config = FastApiConfig()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_connections()

    # add routes to server
    from .routes import router  # noqa: PLC0415

    app.include_router(router, prefix=config.URL_PREFIX)
    logger.info("Server started 🚀")

    yield

    # cleanup on shutdown
    await close_connections()


app = FastAPI(lifespan=lifespan)
register_handlers(app)
register_middlewares(app)
