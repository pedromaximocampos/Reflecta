from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class SentenceThemeModel(Base):
    __tablename__ = "sentence_themes"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_sentence_themes_confidence_range",
        ),
        {"schema": "journal_schema"},
    )

    sentence_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.journal_sentences.id", ondelete="CASCADE"),
        primary_key=True,
    )
    theme_id: Mapped[str] = mapped_column(String(26), primary_key=True)
    theme_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    confirmed_by_user: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
