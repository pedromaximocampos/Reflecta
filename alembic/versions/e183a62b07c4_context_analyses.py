"""Explicit contextual journal analysis."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e183a62b07c4"
down_revision = "a3d9e7f4b612"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("context_analyses",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("entry_ids", postgresql.JSONB(), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "fingerprint", name="uq_context_user_snapshot"),
        schema="journal_schema")

    op.create_index("ix_context_analyses_user_created_id", "context_analyses",
                    ["user_id", "created_at", "id"], schema="journal_schema")


def downgrade():
    op.drop_table("context_analyses", schema="journal_schema")
