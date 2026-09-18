from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        CheckConstraint(
            "length(trim(content_text)) > 0",
            name="ck_journal_entries_content_not_blank",
        ),
        Index(
            "ix_journal_entries_active_user_created_at",
            "user_id",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_journal_entries_status", "status"),
        {"schema": "journal_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    context_tags: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
