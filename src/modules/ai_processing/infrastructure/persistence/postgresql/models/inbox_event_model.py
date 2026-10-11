from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ai_processing.domain.value_objects import InboxEventStatus
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class InboxEventModel(Base):
    __tablename__ = "inbox_events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('processing', 'processed', 'failed')",
            name="ck_ai_inbox_events_valid_status",
        ),
        CheckConstraint(
            "attempts >= 1",
            name="ck_ai_inbox_events_positive_attempts",
        ),
        CheckConstraint(
            "(status = 'processing' AND lease_expires_at IS NOT NULL "
            "AND processed_at IS NULL) OR "
            "(status = 'processed' AND lease_expires_at IS NULL "
            "AND processed_at IS NOT NULL) OR "
            "(status = 'failed' AND lease_expires_at IS NULL "
            "AND processed_at IS NULL)",
            name="ck_ai_inbox_events_lifecycle_fields",
        ),
        Index(
            "ix_ai_inbox_events_status_lease",
            "status",
            "lease_expires_at",
        ),
        {"schema": "ai_processing_schema"},
    )

    consumer_name: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )
    event_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=InboxEventStatus.PROCESSING.value,
        server_default=InboxEventStatus.PROCESSING.value,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    received_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
