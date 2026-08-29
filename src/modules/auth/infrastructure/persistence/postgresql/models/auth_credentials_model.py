from src.modules.auth.infrastructure.persistence.postgresql.models import *
from src.infra.postgresql.configs.base import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, String, TIMESTAMP, func, ForeignKey


class AuthCredentialsModel(Base):
    __tablename__ = "auth_credentials"

    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
                                         unique=True, primary_key=True, index=True)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    password_algorithm: Mapped[str] = mapped_column(String, nullable=False)
    password_version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    last_password_change: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    user: Mapped["UserModel"] = relationship(
        back_populates="credentials",
        lazy="joined",
    )