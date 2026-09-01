from dataclasses import dataclass
from enum import StrEnum

from src.modules.notification.domain.value_objects.recipient_email import RecipientEmail


class EmailKind(StrEnum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


@dataclass(frozen=True, slots=True)
class EmailDTO:
    email: RecipientEmail
    username: str
    link: str
    expires_in_minutes: int
    kind: EmailKind
