from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, MetaData, String, Table, Text, func
from sqlalchemy.orm import registry, relationship

from app.domain import models

metadata = MetaData()


# tables
task_list = Table(
    "task_list",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("version", Integer, nullable=False, default=0),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now()),
    Column("name", String(255), nullable=False, index=True),
    Column("statuses", JSON, nullable=True),
    Column("default_status", String(255), nullable=True),
    Column("user_id", String(255), nullable=False),
)

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("version", Integer, nullable=False, default=0),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now()),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("status", String(255), nullable=False, index=True),
    Column("tags", JSON, nullable=True),
    Column("task_list_id", Integer, ForeignKey("task_list.id"), nullable=False),
)


# register mapping between table and domain models
mapper_registry = registry()


def add_model_mappings() -> None:
    mapper_registry.map_imperatively(
        models.TaskList,
        task_list,
        properties={
            "_pk": task_list.c.id,
            "_version": task_list.c.version,
            "_name": task_list.c.name,
            "_statuses": task_list.c.statuses,
            "_default_status": task_list.c.default_status,
            "_user_id": task_list.c.default_status,
        },
    )
    mapper_registry.map_imperatively(
        models.Task,
        task,
        properties={
            "_pk": task.c.id,
            "_title": task.c.title,
            "_description": task.c.description,
            "_status": task.c.status,
            "_tags": task.c.tags,
            "_task_list": relationship(models.TaskList, lazy="joined"),
        },
    )


def remove_model_mappings() -> None:
    mapper_registry.dispose()
