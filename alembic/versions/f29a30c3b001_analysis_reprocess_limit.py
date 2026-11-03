"""Limit user reprocessing and audit accepted requests (#30)."""
from alembic import op
import sqlalchemy as sa

revision = "f29a30c3b001"
down_revision = "e183a62b07c4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("journal_entries", sa.Column("user_reprocess_count", sa.Integer(), nullable=False, server_default="0"), schema="journal_schema")
    op.create_check_constraint("ck_journal_user_reprocess_limit", "journal_entries", "user_reprocess_count BETWEEN 0 AND 3", schema="journal_schema")
    op.create_table("analysis_reprocess_requests",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("entry_id", sa.String(26), sa.ForeignKey("journal_schema.journal_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("failure_id", sa.String(26), sa.ForeignKey("journal_schema.analysis.id", ondelete="SET NULL"), nullable=True),
        sa.Column("requested_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_role", sa.String(5), nullable=False),
        sa.Column("user_attempt_number", sa.Integer(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("failure_id", name="uq_analysis_reprocess_failure"),
        sa.CheckConstraint("actor_role IN ('USER', 'ADMIN')", name="ck_analysis_reprocess_actor"),
        schema="journal_schema")
    op.create_index("ix_analysis_reprocess_entry_date", "analysis_reprocess_requests", ["entry_id", "requested_at"], schema="journal_schema")


def downgrade():
    op.drop_table("analysis_reprocess_requests", schema="journal_schema")
    op.drop_constraint("ck_journal_user_reprocess_limit", "journal_entries", schema="journal_schema")
    op.drop_column("journal_entries", "user_reprocess_count", schema="journal_schema")
