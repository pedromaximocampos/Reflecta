"""Create secure administrator invitations.

Revision ID: a74c2d900007
Revises: f13a4c600006
Create Date: 2026-11-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a74c2d900007"
down_revision: Union[str, Sequence[str], None] = "f13a4c600006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_invitations",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("target_user_id", sa.String(length=26), nullable=False),
        sa.Column("invited_by_user_id", sa.String(length=26), nullable=False),
        sa.Column("target_email", sa.String(length=255), nullable=False),
        sa.Column("target_username", sa.String(length=255), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["target_user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"], ["users.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_admin_invitations_target_user_id",
        "admin_invitations",
        ["target_user_id"],
    )
    op.create_index(
        "ix_admin_invitations_invited_by_user_id",
        "admin_invitations",
        ["invited_by_user_id"],
    )
    op.create_index(
        "ix_admin_invitations_created_at",
        "admin_invitations",
        ["created_at"],
    )
    op.create_index(
        "uq_admin_invitations_active_per_user",
        "admin_invitations",
        ["target_user_id"],
        unique=True,
        postgresql_where=sa.text("accepted_at IS NULL AND revoked_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_admin_invitations_active_per_user",
        table_name="admin_invitations",
    )
    op.drop_index("ix_admin_invitations_created_at", table_name="admin_invitations")
    op.drop_index(
        "ix_admin_invitations_invited_by_user_id",
        table_name="admin_invitations",
    )
    op.drop_index(
        "ix_admin_invitations_target_user_id",
        table_name="admin_invitations",
    )
    op.drop_table("admin_invitations")
