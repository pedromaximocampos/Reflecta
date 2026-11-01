"""Explicit seven-day contextual analysis periods, minimum five entries."""
from alembic import op
import sqlalchemy as sa
revision = "a31b7d5e0001"
down_revision = "f29a30c3b001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("context_analyses", sa.Column("period_start", sa.Date(), nullable=True), schema="journal_schema")
    op.add_column("context_analyses", sa.Column("period_end", sa.Date(), nullable=True), schema="journal_schema")
    op.create_check_constraint("ck_context_period_seven_days", "context_analyses", "(period_start IS NULL AND period_end IS NULL) OR (period_start IS NOT NULL AND period_end IS NOT NULL AND period_end = period_start + 6)", schema="journal_schema")


def downgrade():
    op.drop_constraint("ck_context_period_seven_days", "context_analyses", schema="journal_schema")
    op.drop_column("context_analyses", "period_end", schema="journal_schema")
    op.drop_column("context_analyses", "period_start", schema="journal_schema")
