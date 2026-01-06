from datetime import datetime, timezone
from dataclasses import dataclass

from src.domain.value_objects.email import Email
from src.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class PasswordResetRequested:
    __event_type__ = "emails.password_reset.requested"

    user_id: UserId
    username: str
    user_email: Email
    raw_code: str
    occurred_at: datetime