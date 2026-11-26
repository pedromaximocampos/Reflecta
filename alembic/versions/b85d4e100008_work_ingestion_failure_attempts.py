"""create durable work ingestion failure attempts

Revision ID: b85d4e100008
Revises: a74c2d900007
"""

from alembic import op
import sqlalchemy as sa


revision = "b85d4e100008"
down_revision = "a74c2d900007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_ingestion_failure_attempts",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("ingestion_id", sa.String(length=26), nullable=False),
        sa.Column("chunk_id", sa.String(length=26), nullable=True),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=128), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("start_page", sa.Integer(), nullable=True),
        sa.Column("end_page", sa.Integer(), nullable=True),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("content_sha256", sa.String(length=64), nullable=True),
        sa.Column("provider_request_id", sa.String(length=128), nullable=True),
        sa.Column("provider_response_id", sa.String(length=128), nullable=True),
        sa.Column("context_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ingestion_id"],
            ["catalog_schema.work_ingestions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["ai_processing_schema.work_ingestion_chunks.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="ai_processing_schema",
    )
    op.create_index(
        "ix_work_ingestion_failure_attempts_ingestion_occurred",
        "work_ingestion_failure_attempts",
        ["ingestion_id", "occurred_at"],
        schema="ai_processing_schema",
    )
    op.create_index(
        "ix_work_ingestion_failure_attempts_chunk_occurred",
        "work_ingestion_failure_attempts",
        ["chunk_id", "occurred_at"],
        schema="ai_processing_schema",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_work_ingestion_failure_attempts_chunk_occurred",
        table_name="work_ingestion_failure_attempts",
        schema="ai_processing_schema",
    )
    op.drop_index(
        "ix_work_ingestion_failure_attempts_ingestion_occurred",
        table_name="work_ingestion_failure_attempts",
        schema="ai_processing_schema",
    )
    op.drop_table(
        "work_ingestion_failure_attempts",
        schema="ai_processing_schema",
    )
