from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    String,
    TIMESTAMP,
    Enum as SAEnum,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base
from src.modules.internal_events.domain.value_objects.outbox_status import OutboxStatus


class OutboxModel(Base):
    __tablename__ = "outbox"

    __table_args__ = (
        Index("ix_outbox_status_created_at", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(26),
        primary_key=True,
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}"
    )

    status: Mapped[OutboxStatus] = mapped_column(
        SAEnum(
            OutboxStatus,
            name="outbox_status_enum",
            native_enum=True
        ),
        nullable=False,
        default=OutboxStatus.PENDING,
        server_default=OutboxStatus.PENDING.value
    )

    attempts: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0"
    )
    event_occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    sent_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    failed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    next_attempt_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True
    )


