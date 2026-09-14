from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.modules.auth.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.domain.value_objects.user_role import UserRole
from src.modules.auth.domain.exceptions.user_custom_exceptions import InvalidUserInfoError


@dataclass(eq=False, slots=True)
class AuthCredentials:
    user_id: UserId
    password: PasswordHash
    created_at: datetime
    last_password_change: Optional[datetime] = None


@dataclass(eq=False, slots=True)
class User:
    id: UserId
    email: Email
    username: str
    name: str
    surname: str
    date_of_birth: date
    created_at: datetime
    auth_credentials: AuthCredentials
    is_email_verified: bool
    role: UserRole = UserRole.USER
    email_verified_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_email_verified(self) -> bool:
        return self.is_email_verified

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"

    def update_last_login(self, last_login_at: datetime) -> None:
        self.last_login_at = last_login_at

    def update_avatar_url(self, avatar_url: str) -> None:
        self.avatar_url = avatar_url

    def update_info(
        self,
        *,
        today: date,
        name: Optional[str] = None,
        surname: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        avatar_url: Optional[str] = None,
    ) -> None:
        if all(
            value is None
            for value in (name, surname, date_of_birth, avatar_url)
        ):
            raise InvalidUserInfoError("At least one user information field is required.")

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise InvalidUserInfoError("Name cannot be empty.")
            if len(normalized_name) > 200:
                raise InvalidUserInfoError("Name cannot exceed 200 characters.")
            self.name = normalized_name

        if surname is not None:
            normalized_surname = surname.strip()
            if not normalized_surname:
                raise InvalidUserInfoError("Surname cannot be empty.")
            if len(normalized_surname) > 200:
                raise InvalidUserInfoError("Surname cannot exceed 200 characters.")
            self.surname = normalized_surname

        if date_of_birth is not None:
            if date_of_birth >= today:
                raise InvalidUserInfoError("Date of birth must be in the past.")
            self.date_of_birth = date_of_birth

        if avatar_url is not None:
            normalized_avatar_url = avatar_url.strip()
            if not normalized_avatar_url:
                raise InvalidUserInfoError("Avatar URL cannot be empty.")
            self.avatar_url = normalized_avatar_url

    def set_credentials(self, credentials: AuthCredentials) -> None:
        self.auth_credentials = credentials

    def verify_password(self, plain_password: str, hasher: IPasswordHasher) -> bool:
        if self.auth_credentials is None:
            return False

        ph = PasswordHash(
            algorithm=self.auth_credentials.password.algorithm,
            hash=self.auth_credentials.password.hash,
            version=self.auth_credentials.password.version,
        )

        return hasher.verify(plain_password, ph)

    def update_last_password_change(self, change_time: datetime) -> None:
        self.auth_credentials.last_password_change = change_time

    def update_auth_credentials(self, new_credentials: PasswordHash, updated_at: datetime) -> None:
        self.auth_credentials.password = new_credentials
        self.auth_credentials.last_password_change = updated_at

    def mark_email_as_verified(self, verified_at: datetime) -> None:
        self.is_email_verified = True
        self.email_verified_at = verified_at

    def mark_as_deleted(self, deleted_at: datetime) -> None:
        self.deleted_at = deleted_at

    def mark_as_recovered(self) -> None:
        self.deleted_at = None
