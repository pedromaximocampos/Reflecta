"""Add the user-facing date of a journal entry.

Revision ID: e91a2d400004
Revises: d8c51a700003
"""

from alembic import op
import sqlalchemy as sa


revision = "e91a2d400004"
down_revision = "d8c51a700003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "journal_entries",
        sa.Column("entry_date", sa.Date(), nullable=True),
        schema="journal_schema",
    )
    op.execute(
        """
        UPDATE journal_schema.journal_entries
        SET entry_date = (created_at AT TIME ZONE 'America/Sao_Paulo')::date
        WHERE entry_date IS NULL
        """
    )
    op.alter_column(
        "journal_entries",
        "entry_date",
        nullable=False,
        schema="journal_schema",
    )
    op.create_index(
        "ix_journal_entries_active_user_entry_date",
        "journal_entries",
        ["user_id", "entry_date", "created_at"],
        unique=False,
        schema="journal_schema",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_journal_entries_active_user_entry_date",
        table_name="journal_entries",
        schema="journal_schema",
    )
    op.drop_column(
        "journal_entries",
        "entry_date",
        schema="journal_schema",
    )
