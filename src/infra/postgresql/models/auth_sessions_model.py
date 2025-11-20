from src.infra.postgresql.models import *
from src.infra.postgresql.configs.base import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, String, TIMESTAMP, func, ForeignKey


class AuthSessionsModel(Base):

    __tablename__ = 'auth_sessions'

    id: Mapped[str] = mapped_column(String(26), primary_key=True,nullable=False)
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id",  ondelete="CASCADE") , nullable=False, index=True)

    issued_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    refresh_jti_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )


    user: Mapped["UserModel"] = relationship(
        back_populates="sessions",
        lazy="joined",
    )