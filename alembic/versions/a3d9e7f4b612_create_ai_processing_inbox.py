"""create ai processing inbox events

Revision ID: a3d9e7f4b612
Revises: f6c2a91d4e08
Create Date: 2026-10-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3d9e7f4b612"
down_revision: Union[str, Sequence[str], None] = "f6c2a91d4e08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ai_processing_schema")
    op.create_table(
        "inbox_events",
        sa.Column("consumer_name", sa.String(length=128), nullable=False),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'processing'"),
            nullable=False,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column("received_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("lease_expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('processing', 'processed', 'failed')",
            name="ck_ai_inbox_events_valid_status",
        ),
        sa.CheckConstraint(
            "attempts >= 1",
            name="ck_ai_inbox_events_positive_attempts",
        ),
        sa.CheckConstraint(
            "(status = 'processing' AND lease_expires_at IS NOT NULL "
            "AND processed_at IS NULL) OR "
            "(status = 'processed' AND lease_expires_at IS NULL "
            "AND processed_at IS NOT NULL) OR "
            "(status = 'failed' AND lease_expires_at IS NULL "
            "AND processed_at IS NULL)",
            name="ck_ai_inbox_events_lifecycle_fields",
        ),
        sa.PrimaryKeyConstraint("consumer_name", "event_id"),
        schema="ai_processing_schema",
    )
    op.create_index(
        "ix_ai_inbox_events_status_lease",
        "inbox_events",
        ["status", "lease_expires_at"],
        unique=False,
        schema="ai_processing_schema",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ai_inbox_events_status_lease",
        table_name="inbox_events",
        schema="ai_processing_schema",
    )
    op.drop_table("inbox_events", schema="ai_processing_schema")
