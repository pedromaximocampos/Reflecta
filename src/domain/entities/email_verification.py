from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from src.domain.value_objects.user_id import UserId


@dataclass(slots=True)
class EmailVerification:
    id: str
    user_id: UserId
    token_hash: str
    created_at: datetime
    expires_at: datetime
    verified_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


    @property
    def is_active(self) -> bool:
        return self.verified_at is not None and self.revoked_at is None and self.expires_at > datetime.now(timezone.utc)


    def verify(self, verified_at: datetime) -> None:
        self.verified_at = verified_at