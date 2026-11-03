from datetime import date, datetime
from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class ContextAnalysisModel(Base):
    __tablename__ = "context_analyses"
    __table_args__ = (UniqueConstraint("user_id", "fingerprint", name="uq_context_user_snapshot"),
                      Index("ix_context_analyses_user_created_id", "user_id", "created_at", "id"),
                      CheckConstraint("(period_start IS NULL AND period_end IS NULL) OR (period_start IS NOT NULL AND period_end IS NOT NULL AND period_end = period_start + 6)", name="ck_context_period_seven_days"),
                      {"schema": "journal_schema"})
    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    fingerprint: Mapped[str] = mapped_column(String(64))
    entry_ids: Mapped[list] = mapped_column(JSONB)
    result: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    period_start: Mapped[date | None] = mapped_column(Date)
    period_end: Mapped[date | None] = mapped_column(Date)
