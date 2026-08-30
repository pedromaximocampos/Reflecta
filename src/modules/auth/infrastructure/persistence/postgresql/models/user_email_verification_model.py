from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Index,
    and_,
)
from sqlalchemy.orm import Mapped, relationship
from src.modules.auth.infrastructure.persistence.postgresql.models import *
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


class UserEmailVerificationModel(Base):
    __tablename__ = "user_email_verifications"

    id: Mapped[str] = Column(String(26), primary_key=True, nullable=False)

    user_id: Mapped[str] = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = Column(String(128), unique=True, nullable=False)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relação N:1 (muitas verificações para um usuário)
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="email_verifications",
        lazy="joined",
    )

    __table_args__ = (
        # garante no máximo UM token "ativo" por user:
        # ativo = não verificado e não revogado
        Index(
            "uq_user_email_verifications_active_per_user",
            user_id,
            unique=True,
            postgresql_where=and_(
                verified_at.is_(None),
                revoked_at.is_(None),
            ),
        ),
    )
