"""Merge migration lines and persist per-attempt administrator AI settings."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "d8c51a700003"
down_revision = ("b31c72e00002", "c7e2b4a91d08")
branch_labels = None
depends_on = None


def upgrade():
    for name in ("journal_entries", "analysis_reprocess_requests"):
        op.add_column(name, sa.Column("processing_settings", JSONB(), nullable=True), schema="journal_schema")


def downgrade():
    for name in ("analysis_reprocess_requests", "journal_entries"):
        op.drop_column(name, "processing_settings", schema="journal_schema")
