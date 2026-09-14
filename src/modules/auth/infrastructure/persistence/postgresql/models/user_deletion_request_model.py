from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, TIMESTAMP, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class UserDeletionRequestModel(Base):
    __tablename__ = "user_deletion_requests"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="deletion_requests",
        lazy="joined",
    )

    __table_args__ = (
        Index(
            "uq_user_deletion_requests_active_per_user",
            user_id,
            unique=True,
            postgresql_where=and_(
                confirmed_at.is_(None),
                revoked_at.is_(None),
            ),
        ),
    )
