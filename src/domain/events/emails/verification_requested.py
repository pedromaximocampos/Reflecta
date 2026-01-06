from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.value_objects.email import Email
from src.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class EmailVerificationRequested:
    __event_type__ = "emails.verification.requested"

    user_id: UserId
    username: str
    user_email: Email
    raw_code: str
    occurred_at: datetime
