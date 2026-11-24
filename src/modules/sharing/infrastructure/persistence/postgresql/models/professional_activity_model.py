from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class ProfessionalActivityModel(Base):
    __tablename__ = "professional_activities"
    __table_args__ = (
        Index(
            "ix_professional_activities_user_status_created",
            "user_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_professional_activities_share_created",
            "share_id",
            "created_at",
        ),
        {"schema": "sharing_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    share_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey(
            "journal_schema.context_analysis_shares.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

