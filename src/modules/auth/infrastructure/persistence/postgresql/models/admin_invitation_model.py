from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, TIMESTAMP, and_
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class AdminInvitationModel(Base):
    __tablename__ = "admin_invitations"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, nullable=False)
    target_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    invited_by_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    target_email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_username: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    __table_args__ = (
        Index("ix_admin_invitations_target_user_id", target_user_id),
        Index("ix_admin_invitations_invited_by_user_id", invited_by_user_id),
        Index("ix_admin_invitations_created_at", created_at),
        Index(
            "uq_admin_invitations_active_per_user",
            target_user_id,
            unique=True,
            postgresql_where=and_(accepted_at.is_(None), revoked_at.is_(None)),
        ),
    )
