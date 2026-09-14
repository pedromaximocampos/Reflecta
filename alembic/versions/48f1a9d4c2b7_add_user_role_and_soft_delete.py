"""add user role and soft delete

Revision ID: 48f1a9d4c2b7
Revises: ca9163c93ce6
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "48f1a9d4c2b7"
down_revision: Union[str, Sequence[str], None] = "ca9163c93ce6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = postgresql.ENUM(
        "USER",
        "ADMIN",
        name="user_role_enum",
        create_type=False,
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            server_default="USER",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_users_active_role",
        "users",
        ["role"],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_active_role", table_name="users")
    op.drop_column("users", "deleted_at")
    op.drop_column("users", "role")

    user_role_enum = postgresql.ENUM(
        "USER",
        "ADMIN",
        name="user_role_enum",
        create_type=False,
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)
