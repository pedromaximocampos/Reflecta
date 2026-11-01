from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class AnalysisReprocessModel(Base):
    __tablename__ = "analysis_reprocess_requests"
    __table_args__ = (
        UniqueConstraint("failure_id", name="uq_analysis_reprocess_failure"),
        CheckConstraint("actor_role IN ('USER', 'ADMIN')", name="ck_analysis_reprocess_actor"),
        Index("ix_analysis_reprocess_entry_date", "entry_id", "requested_at"),
        {"schema": "journal_schema"},
    )
    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    entry_id: Mapped[str] = mapped_column(String(26), ForeignKey("journal_schema.journal_entries.id", ondelete="CASCADE"))
    failure_id: Mapped[str | None] = mapped_column(String(26), ForeignKey("journal_schema.analysis.id", ondelete="SET NULL"))
    requested_by: Mapped[str | None] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"))
    actor_role: Mapped[str] = mapped_column(String(5))
    user_attempt_number: Mapped[int | None] = mapped_column(Integer)
    requested_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    processing_settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
