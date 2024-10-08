from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry

from app.domain import models

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("version", Integer, nullable=False, default=0),
    Column("email", String, nullable=False, unique=True, index=True),
)

# register mapping between table and domain models
mapper_registry = registry()


def add_model_mappings():
    mapper_registry.map_imperatively(models.User, user)


def remove_model_mappings():
    mapper_registry.dispose()
