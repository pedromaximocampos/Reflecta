from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class WorkIngestionModel(Base):
    __tablename__ = "work_ingestions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'pending_review', 'completed', 'failed')",
            name="ck_work_ingestions_valid_status",
        ),
        CheckConstraint(
            "attempts >= 0",
            name="ck_work_ingestions_non_negative_attempts",
        ),
        Index(
            "ix_work_ingestions_work_created_at",
            "work_id",
            "created_at",
        ),
        Index(
            "ix_work_ingestions_status_created_at",
            "status",
            "created_at",
        ),
        {"schema": "catalog_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(26), nullable=False)
    requested_by: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    s3_bucket: Mapped[str] = mapped_column(String(63), nullable=False)
    s3_object_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=WorkIngestionStatus.PENDING.value,
        server_default=WorkIngestionStatus.PENDING.value,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
