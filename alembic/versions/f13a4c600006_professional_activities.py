"""Create professional activities for shared analyses.

Revision ID: f13a4c600006
Revises: f02b3c400005
"""

from alembic import op
import sqlalchemy as sa


revision = "f13a4c600006"
down_revision = "f02b3c400005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS sharing_schema")
    op.create_table(
        "professional_activities",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "share_id",
            sa.String(26),
            sa.ForeignKey(
                "journal_schema.context_analysis_shares.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "kind IN ('activity', 'guided_reflection')",
            name="ck_professional_activities_kind",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'completed')",
            name="ck_professional_activities_status",
        ),
        schema="sharing_schema",
    )
    op.create_index(
        "ix_professional_activities_user_status_created",
        "professional_activities",
        ["user_id", "status", "created_at"],
        schema="sharing_schema",
    )
    op.create_index(
        "ix_professional_activities_share_created",
        "professional_activities",
        ["share_id", "created_at"],
        schema="sharing_schema",
    )


def downgrade() -> None:
    op.drop_table("professional_activities", schema="sharing_schema")
    op.execute("DROP SCHEMA IF EXISTS sharing_schema")

