from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class JournalSentenceModel(Base):
    __tablename__ = "journal_sentences"
    __table_args__ = (
        UniqueConstraint(
            "analysis_id",
            "sentence_index",
            name="uq_journal_sentences_analysis_index",
        ),
        CheckConstraint(
            "sentence_index >= 0",
            name="ck_journal_sentences_non_negative_index",
        ),
        CheckConstraint(
            "start_offset >= 0 AND end_offset >= start_offset",
            name="ck_journal_sentences_valid_offsets",
        ),
        Index("ix_journal_sentences_entry_id", "journal_entry_id"),
        Index("ix_journal_sentences_analysis_id", "analysis_id"),
        {"schema": "journal_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    journal_entry_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.journal_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.analysis.id", ondelete="CASCADE"),
        nullable=False,
    )
    sentence_index: Mapped[int] = mapped_column(nullable=False)
    sentence_text: Mapped[str] = mapped_column(Text, nullable=False)
    start_offset: Mapped[int] = mapped_column(nullable=False)
    end_offset: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
