from src.infra.postgresql.models import *


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    credentials: Mapped["AuthCredentialsModel"] = relationship(
        back_populates="user",
        uselist=False,  # <- importante: indica relação 1:1
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, username={self.username}, email={self.email})"