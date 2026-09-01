from dataclasses import dataclass
from enum import StrEnum

from src.modules.auth.public.email import Email


class EmailKind(StrEnum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


@dataclass(frozen=True, slots=True)
class EmailDTO:
    email: Email
    username: str
    link: str
    expires_in_minutes: int
    kind: EmailKind
