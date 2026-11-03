"""add user avatar object key

Revision ID: c7e2b4a91d08
Revises: a3d9e7f4b612
Create Date: 2026-10-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c7e2b4a91d08"
down_revision: Union[str, Sequence[str], None] = "a3d9e7f4b612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("avatar_object_key", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "avatar_object_key")
