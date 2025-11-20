from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Optional

from src.domain.value_objects.token_jti import TokenJti
from src.domain.value_objects.user_id import UserId


@dataclass(eq=False, slots=True)
class AuthSession:
    id: str
    user_id: UserId
    issued_at: datetime
    expires_at: datetime
    refresh_jti_hash: TokenJti
    updated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and datetime.now(timezone.utc) < self.expires_at

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at