from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class EntryEmbeddingModel(Base):
    __tablename__ = "entry_embeddings"
    __table_args__ = {"schema": "journal_schema"}

    entry_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("journal_schema.journal_entries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
