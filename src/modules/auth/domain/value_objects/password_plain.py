from dataclasses import dataclass
import re

from src.shared.config.settings import get_settings
from src.modules.auth.domain.exceptions.passwords_exceptions import WeekPasswordException
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.domain.ports.security.ipassword_hasher import IPasswordHasher

_settings = get_settings()

@dataclass(frozen=True, slots=True)
class PasswordPlain:
    value: str

    def __post_init__(self) -> None:
        v = self.value

        if len(v) < _settings.MINIMUM_PASSWORD_LENGTH:
            raise WeekPasswordException(f"Password must have at least {_settings.PASSWORD_MIN_LENGTH} characters.")
        if not re.search(r"[A-Za-z]", v):
            raise WeekPasswordException("Password must contain at least one letter.")
        if not re.search(r"\d", v):
            raise WeekPasswordException("Password must contain at least one number.")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise WeekPasswordException("Password must contain at least one special character.")

    def to_hash(self, hasher: IPasswordHasher) -> PasswordHash:
        return hasher.hash(self.value)

    def __repr__(self) -> str:
        return "PasswordPlain(**redacted**)"