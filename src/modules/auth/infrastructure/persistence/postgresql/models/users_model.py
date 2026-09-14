from datetime import date, datetime
from src.modules.auth.infrastructure.persistence.postgresql.models import *
from sqlalchemy import DATE, Enum as SAEnum, Index, String, TIMESTAMP, func, text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.modules.auth.domain.value_objects.user_role import UserRole
from src.shared.infrastructure.persistence.postgresql.configs.base import Base
from src.modules.auth.infrastructure.persistence.postgresql.models.reset_password_model import ResetPasswordModel


class UserModel(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index(
            "ix_users_active_role",
            "role",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    surname: Mapped[str] = mapped_column(String(200), unique=False, index=False, nullable=True)
    date_of_birth: Mapped[date] = mapped_column(DATE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role_enum", native_enum=True),
        nullable=False,
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )

    is_email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    email_verified_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

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

    password_resets: Mapped[list[ResetPasswordModel]] = relationship(
        "ResetPasswordModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    deletion_requests: Mapped[list["UserDeletionRequestModel"]] = relationship(
        "UserDeletionRequestModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    recovery_requests: Mapped[list["UserRecoveryRequestModel"]] = relationship(
        "UserRecoveryRequestModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, username={self.username}, email={self.email})"
