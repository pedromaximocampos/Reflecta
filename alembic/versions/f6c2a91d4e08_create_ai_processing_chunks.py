"""create ai processing work ingestion chunks

Revision ID: f6c2a91d4e08
Revises: b81f4e2a9c07
Create Date: 2026-10-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6c2a91d4e08"
down_revision: Union[str, Sequence[str], None] = "b81f4e2a9c07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ai_processing_schema")
    op.create_table(
        "work_ingestion_chunks",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("ingestion_id", sa.String(length=26), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("start_page", sa.Integer(), nullable=False),
        sa.Column("end_page", sa.Integer(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("chunker_version", sa.String(length=64), nullable=False),
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
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("lease_expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_work_ingestion_chunks_valid_status",
        ),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name="ck_work_ingestion_chunks_non_negative_index",
        ),
        sa.CheckConstraint(
            "start_page >= 1 AND end_page >= start_page",
            name="ck_work_ingestion_chunks_valid_pages",
        ),
        sa.CheckConstraint(
            "start_offset >= 0 AND end_offset > start_offset",
            name="ck_work_ingestion_chunks_valid_offsets",
        ),
        sa.CheckConstraint(
            "attempts >= 0",
            name="ck_work_ingestion_chunks_non_negative_attempts",
        ),
        sa.CheckConstraint(
            "((status = 'processing' AND lease_expires_at IS NOT NULL) OR "
            "(status <> 'processing' AND lease_expires_at IS NULL))",
            name="ck_work_ingestion_chunks_processing_lease",
        ),
        sa.ForeignKeyConstraint(
            ["ingestion_id"],
            ["catalog_schema.work_ingestions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ingestion_id",
            "chunk_index",
            name="uq_work_ingestion_chunks_ingestion_index",
        ),
        schema="ai_processing_schema",
    )
    op.create_index(
        "ix_work_ingestion_chunks_ingestion_status_index",
        "work_ingestion_chunks",
        ["ingestion_id", "status", "chunk_index"],
        unique=False,
        schema="ai_processing_schema",
    )
    op.create_index(
        "ix_work_ingestion_chunks_status_lease",
        "work_ingestion_chunks",
        ["status", "lease_expires_at"],
        unique=False,
        schema="ai_processing_schema",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_work_ingestion_chunks_status_lease",
        table_name="work_ingestion_chunks",
        schema="ai_processing_schema",
    )
    op.drop_index(
        "ix_work_ingestion_chunks_ingestion_status_index",
        table_name="work_ingestion_chunks",
        schema="ai_processing_schema",
    )
    op.drop_table("work_ingestion_chunks", schema="ai_processing_schema")
    op.execute("DROP SCHEMA IF EXISTS ai_processing_schema")
