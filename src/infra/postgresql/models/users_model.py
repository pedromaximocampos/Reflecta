from datetime import date, datetime
from src.infra.postgresql.models import *
from sqlalchemy import String, TIMESTAMP, DATE, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.infra.postgresql.configs.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    surname: Mapped[str] = mapped_column(String(200), unique=False, index=False, nullable=True)
    date_of_birth: Mapped[date] = mapped_column(DATE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

    is_email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    email_verified_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    credentials: Mapped[AuthCredentialsModel] = relationship(
        "AuthCredentialsModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    sessions: Mapped[list["AuthSessionsModel"]] = relationship(
        "AuthSessionsModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # agora 1:N: um user pode ter várias verificações ao longo do tempo
    email_verifications: Mapped[list["UserEmailVerificationModel"]] = relationship(
        "UserEmailVerificationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, username={self.username}, email={self.email})"
