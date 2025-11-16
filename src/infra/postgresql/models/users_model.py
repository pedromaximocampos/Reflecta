from src.infra.postgresql.models import *
from datetime import datetime, date

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(DATE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    credentials: Mapped["AuthCredentialsModel"] = relationship(
        back_populates="user",
        uselist=False,  # <- importante: indica relação 1:1
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    sessions: Mapped[list["AuthSessionsModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"UserModel(id={self.id}, username={self.username}, email={self.email})"