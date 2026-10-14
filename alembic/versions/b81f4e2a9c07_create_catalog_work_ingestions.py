"""create catalog work ingestions

Revision ID: b81f4e2a9c07
Revises: d4a1c7e9b203
Create Date: 2026-10-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b81f4e2a9c07"
down_revision: Union[str, Sequence[str], None] = "d4a1c7e9b203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS catalog_schema")
    op.create_table(
        "work_ingestions",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("work_id", sa.String(length=26), nullable=False),
        sa.Column("requested_by", sa.String(length=26), nullable=False),
        sa.Column("s3_bucket", sa.String(length=63), nullable=False),
        sa.Column("s3_object_key", sa.String(length=1024), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'pending_review', 'completed', 'failed')",
            name="ck_work_ingestions_valid_status",
        ),
        sa.CheckConstraint(
            "attempts >= 0",
            name="ck_work_ingestions_non_negative_attempts",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="catalog_schema",
    )
    op.create_index(
        "ix_work_ingestions_work_created_at",
        "work_ingestions",
        ["work_id", "created_at"],
        unique=False,
        schema="catalog_schema",
    )
    op.create_index(
        "ix_work_ingestions_status_created_at",
        "work_ingestions",
        ["status", "created_at"],
        unique=False,
        schema="catalog_schema",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_work_ingestions_status_created_at",
        table_name="work_ingestions",
        schema="catalog_schema",
    )
    op.drop_index(
        "ix_work_ingestions_work_created_at",
        table_name="work_ingestions",
        schema="catalog_schema",
    )
    op.drop_table("work_ingestions", schema="catalog_schema")
    op.execute("DROP SCHEMA IF EXISTS catalog_schema")
