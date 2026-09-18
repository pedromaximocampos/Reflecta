from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class AnalysisModel(Base):
    __tablename__ = "analysis"
    __table_args__ = (
        Index("ix_analysis_entry_created_at", "journal_entry_id", "created_at"),
        {"schema": "journal_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    journal_entry_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.journal_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    analyzed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
