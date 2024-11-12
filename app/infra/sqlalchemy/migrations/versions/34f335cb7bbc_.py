"""Init

Revision ID: 34f335cb7bbc
Revises:
Create Date: 2024-11-03 15:39:38.673251

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "34f335cb7bbc"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "task_list",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("statuses", sa.JSON(), nullable=True),
        sa.Column("default_status", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=False, index=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("task_list_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["task_list_id"], ["task_list.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("task")
    op.drop_table("task_list")
    # ### end Alembic commands ###
