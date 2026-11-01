from datetime import datetime
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class ContextShareModel(Base):
    __tablename__ = "context_analysis_shares"
    __table_args__ = (Index("ix_context_shares_owner_analysis", "user_id", "analysis_id"), {"schema": "journal_schema"})
    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    analysis_id: Mapped[str] = mapped_column(String(26), ForeignKey("journal_schema.context_analyses.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    snapshot: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
