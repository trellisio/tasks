from sys import stderr
from typing import Literal

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings

type LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]


class LoggingConfig(BaseSettings):
    LOG_LEVEL: LogLevel = Field(
        description="Logging level (https://docs.python.org/3/library/logging.html#logging-levels)",
        default="DEBUG",
    )


config = LoggingConfig()

logger.remove()
logger.add(
    stderr,
    colorize=True,
    format="{time} {level} {message}",
    level=config.LOG_LEVEL,
)
