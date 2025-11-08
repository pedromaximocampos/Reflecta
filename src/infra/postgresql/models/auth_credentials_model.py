from src.infra.postgresql.models import *



class AuthCredentialsModel(Base):
    __tablename__ = "auth_credentials"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False,
                                         unique=True, ondelete="CASCADE", primary_key=True, index=True)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    password_algorithm: Mapped[str] = mapped_column(String, nullable=False)
    password_version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    last_password_change: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)