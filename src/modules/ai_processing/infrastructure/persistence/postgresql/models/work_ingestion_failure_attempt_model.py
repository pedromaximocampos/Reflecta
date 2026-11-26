from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class WorkIngestionFailureAttemptModel(Base):
    __tablename__ = "work_ingestion_failure_attempts"
    __table_args__ = (
        Index(
            "ix_work_ingestion_failure_attempts_ingestion_occurred",
            "ingestion_id",
            "occurred_at",
        ),
        Index(
            "ix_work_ingestion_failure_attempts_chunk_occurred",
            "chunk_id",
            "occurred_at",
        ),
        {"schema": "ai_processing_schema"},
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    ingestion_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("catalog_schema.work_ingestions.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey(
            "ai_processing_schema.work_ingestion_chunks.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    error_code: Mapped[str] = mapped_column(String(128), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    start_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_response_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    context_text: Mapped[str | None] = mapped_column(Text, nullable=True)
