from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class WorkIngestionChunkModel(Base):
    __tablename__ = "work_ingestion_chunks"
    __table_args__ = (
        UniqueConstraint(
            "ingestion_id",
            "chunk_index",
            name="uq_work_ingestion_chunks_ingestion_index",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_work_ingestion_chunks_valid_status",
        ),
        CheckConstraint(
            "chunk_index >= 0",
            name="ck_work_ingestion_chunks_non_negative_index",
        ),
        CheckConstraint(
            "start_page >= 1 AND end_page >= start_page",
            name="ck_work_ingestion_chunks_valid_pages",
        ),
        CheckConstraint(
            "start_offset >= 0 AND end_offset > start_offset",
            name="ck_work_ingestion_chunks_valid_offsets",
        ),
        CheckConstraint(
            "attempts >= 0",
            name="ck_work_ingestion_chunks_non_negative_attempts",
        ),
        CheckConstraint(
            "((status = 'processing' AND lease_expires_at IS NOT NULL) OR "
            "(status <> 'processing' AND lease_expires_at IS NULL))",
            name="ck_work_ingestion_chunks_processing_lease",
        ),
        Index(
            "ix_work_ingestion_chunks_ingestion_status_index",
            "ingestion_id",
            "status",
            "chunk_index",
        ),
        Index(
            "ix_work_ingestion_chunks_status_lease",
            "status",
            "lease_expires_at",
        ),
        {"schema": "ai_processing_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    ingestion_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey(
            "catalog_schema.work_ingestions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_page: Mapped[int] = mapped_column(Integer, nullable=False)
    end_page: Mapped[int] = mapped_column(Integer, nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    chunker_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=WorkIngestionChunkStatus.PENDING.value,
        server_default=WorkIngestionChunkStatus.PENDING.value,
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
    updated_at: Mapped[datetime] = mapped_column(
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
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
