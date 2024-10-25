from sqlalchemy import UUID, Column, Integer, MetaData, Table
from sqlalchemy.orm import registry

from app.domain import models

metadata = MetaData()

# tables
task_list = Table(
    "task_list",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("version", Integer, nullable=False, default=0),
    Column("identifier", UUID, nullable=False, unique=True, index=True),
)

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("version", Integer, nullable=False, default=0),
)


# register mapping between table and domain models
mapper_registry = registry()


def add_model_mappings() -> None:
    mapper_registry.map_imperatively(models.TaskList, task_list)
    mapper_registry.map_imperatively(models.Task, task)


def remove_model_mappings() -> None:
    mapper_registry.dispose()
