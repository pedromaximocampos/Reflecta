"""create journal schema

Revision ID: d4a1c7e9b203
Revises: 9c4f12a7e6d3
Create Date: 2026-09-18

"""
from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d4a1c7e9b203"
down_revision: Union[str, Sequence[str], None] = "9c4f12a7e6d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS journal_schema")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("user_id", sa.String(length=26), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("context_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint(
            "length(trim(content_text)) > 0",
            name="ck_journal_entries_content_not_blank",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="journal_schema",
    )
    op.create_index(
        "ix_journal_entries_active_user_created_at",
        "journal_entries",
        ["user_id", "created_at"],
        unique=False,
        schema="journal_schema",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_journal_entries_status",
        "journal_entries",
        ["status"],
        unique=False,
        schema="journal_schema",
    )

    op.create_table(
        "analysis",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("journal_entry_id", sa.String(length=26), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("main_message", sa.Text(), nullable=True),
        sa.Column("content_meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("analyzed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("analysis_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["journal_schema.journal_entries.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="journal_schema",
    )
    op.create_index(
        "ix_analysis_entry_created_at",
        "analysis",
        ["journal_entry_id", "created_at"],
        unique=False,
        schema="journal_schema",
    )

    op.create_table(
        "journal_sentences",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("journal_entry_id", sa.String(length=26), nullable=False),
        sa.Column("analysis_id", sa.String(length=26), nullable=False),
        sa.Column("sentence_index", sa.Integer(), nullable=False),
        sa.Column("sentence_text", sa.Text(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.CheckConstraint(
            "sentence_index >= 0",
            name="ck_journal_sentences_non_negative_index",
        ),
        sa.CheckConstraint(
            "start_offset >= 0 AND end_offset >= start_offset",
            name="ck_journal_sentences_valid_offsets",
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["journal_schema.analysis.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["journal_schema.journal_entries.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "analysis_id",
            "sentence_index",
            name="uq_journal_sentences_analysis_index",
        ),
        schema="journal_schema",
    )
    op.create_index(
        "ix_journal_sentences_analysis_id",
        "journal_sentences",
        ["analysis_id"],
        unique=False,
        schema="journal_schema",
    )
    op.create_index(
        "ix_journal_sentences_entry_id",
        "journal_sentences",
        ["journal_entry_id"],
        unique=False,
        schema="journal_schema",
    )

    op.create_table(
        "sentence_themes",
        sa.Column("sentence_id", sa.String(length=26), nullable=False),
        sa.Column("theme_id", sa.String(length=26), nullable=False),
        sa.Column("theme_slug", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column(
            "confirmed_by_user",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_sentence_themes_confidence_range",
        ),
        sa.ForeignKeyConstraint(
            ["sentence_id"],
            ["journal_schema.journal_sentences.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("sentence_id", "theme_id"),
        schema="journal_schema",
    )

    op.create_table(
        "sentence_passages",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("sentence_id", sa.String(length=26), nullable=False),
        sa.Column("passage_id", sa.String(length=26), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "payload_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_sentence_passages_confidence_range",
        ),
        sa.ForeignKeyConstraint(
            ["sentence_id"],
            ["journal_schema.journal_sentences.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sentence_id",
            "passage_id",
            name="uq_sentence_passages_sentence_passage",
        ),
        schema="journal_schema",
    )

    op.create_table(
        "entry_embeddings",
        sa.Column("entry_id", sa.String(length=26), nullable=False),
        sa.Column("embedding", Vector(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["entry_id"],
            ["journal_schema.journal_entries.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("entry_id"),
        schema="journal_schema",
    )

    op.create_table(
        "sentence_embeddings",
        sa.Column("sentence_id", sa.String(length=26), nullable=False),
        sa.Column("embedding", Vector(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sentence_id"],
            ["journal_schema.journal_sentences.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("sentence_id"),
        schema="journal_schema",
    )


def downgrade() -> None:
    op.drop_table("sentence_embeddings", schema="journal_schema")
    op.drop_table("entry_embeddings", schema="journal_schema")
    op.drop_table("sentence_passages", schema="journal_schema")
    op.drop_table("sentence_themes", schema="journal_schema")
    op.drop_index(
        "ix_journal_sentences_entry_id",
        table_name="journal_sentences",
        schema="journal_schema",
    )
    op.drop_index(
        "ix_journal_sentences_analysis_id",
        table_name="journal_sentences",
        schema="journal_schema",
    )
    op.drop_table("journal_sentences", schema="journal_schema")
    op.drop_index(
        "ix_analysis_entry_created_at",
        table_name="analysis",
        schema="journal_schema",
    )
    op.drop_table("analysis", schema="journal_schema")
    op.drop_index(
        "ix_journal_entries_status",
        table_name="journal_entries",
        schema="journal_schema",
    )
    op.drop_index(
        "ix_journal_entries_active_user_created_at",
        table_name="journal_entries",
        schema="journal_schema",
    )
    op.drop_table("journal_entries", schema="journal_schema")
    op.execute("DROP SCHEMA IF EXISTS journal_schema")
