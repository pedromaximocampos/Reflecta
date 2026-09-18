from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class SentencePassageModel(Base):
    __tablename__ = "sentence_passages"
    __table_args__ = (
        UniqueConstraint(
            "sentence_id",
            "passage_id",
            name="uq_sentence_passages_sentence_passage",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_sentence_passages_confidence_range",
        ),
        {"schema": "journal_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    sentence_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.journal_sentences.id", ondelete="CASCADE"),
        nullable=False,
    )
    passage_id: Mapped[str] = mapped_column(String(26), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
