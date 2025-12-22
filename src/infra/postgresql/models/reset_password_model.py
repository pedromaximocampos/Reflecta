from sqlalchemy import String, ForeignKey, TIMESTAMP, func

from src.infra.postgresql.models import *
from src.infra.postgresql.configs.base import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship


class ResetPasswordModel(Base):

    __tablename__ = 'passwords_reset'

    id: Mapped[str] = mapped_column(String(26), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id",  ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="email_verifications",
        lazy="joined",
    )

    token_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    used_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

