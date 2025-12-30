from dataclasses import dataclass
from src.domain.value_objects.email import Email

@dataclass(frozen=True, slots=True)
class EmailVerificationDTO:
    raw_code: str
    email: Email
    expires_in_minutes: int
    username: str
    verification_link: str


@dataclass(frozen=True, slots=True)
class EmailPasswordResetDTO:
    raw_code: str
    email: Email
    expires_in_minutes: int
    username: str
    reset_password_link: str
