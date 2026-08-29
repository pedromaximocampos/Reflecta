from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from src.modules.auth.public.user_id import UserId


@dataclass(slots=True)
class ResetPassword:
    id: str
    user_id: UserId
    token_hash: str
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None


    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def mark_as_used(self, now: datetime) -> None:
       self.used_at = now
