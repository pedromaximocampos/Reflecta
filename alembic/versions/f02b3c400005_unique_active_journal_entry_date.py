"""Ensure one active journal entry per user and date.

Revision ID: f02b3c400005
Revises: e91a2d400004
"""

from alembic import op
import sqlalchemy as sa


revision = "f02b3c400005"
down_revision = "e91a2d400004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM journal_schema.journal_entries
                WHERE deleted_at IS NULL
                GROUP BY user_id, entry_date
                HAVING COUNT(*) > 1
            ) THEN
                RAISE EXCEPTION
                    'Cannot enforce one active journal entry per day: duplicate user/date rows exist.';
            END IF;
        END
        $$;
        """
    )
    op.create_index(
        "uq_journal_entries_active_user_entry_date",
        "journal_entries",
        ["user_id", "entry_date"],
        unique=True,
        schema="journal_schema",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_journal_entries_active_user_entry_date",
        table_name="journal_entries",
        schema="journal_schema",
    )
