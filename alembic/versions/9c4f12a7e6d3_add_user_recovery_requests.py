"""add user recovery requests

Revision ID: 9c4f12a7e6d3
Revises: 7b82d9e3a104
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4f12a7e6d3"
down_revision: Union[str, Sequence[str], None] = "7b82d9e3a104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_recovery_requests",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_user_recovery_requests_user_id",
        "user_recovery_requests",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_user_recovery_requests_active_per_user",
        "user_recovery_requests",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("confirmed_at IS NULL AND revoked_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_user_recovery_requests_active_per_user",
        table_name="user_recovery_requests",
    )
    op.drop_index(
        "ix_user_recovery_requests_user_id",
        table_name="user_recovery_requests",
    )
    op.drop_table("user_recovery_requests")
