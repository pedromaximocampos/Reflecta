"""Revocable three-day context analysis links (#31)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
revision = "b31c72e00002"
down_revision = "a31b7d5e0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("context_analysis_shares",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analysis_id", sa.String(26), sa.ForeignKey("journal_schema.context_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("snapshot", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True), schema="journal_schema")
    op.create_index("ix_context_shares_owner_analysis", "context_analysis_shares", ["user_id", "analysis_id"], schema="journal_schema")


def downgrade():
    op.drop_table("context_analysis_shares", schema="journal_schema")
