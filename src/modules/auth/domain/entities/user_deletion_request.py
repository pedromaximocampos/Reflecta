from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.modules.auth.public.user_id import UserId


@dataclass(slots=True)
class UserDeletionRequest:
    id: str
    user_id: UserId
    token_hash: str
    created_at: datetime
    expires_at: datetime
    confirmed_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at <= now

    def confirm(self, confirmed_at: datetime) -> None:
        self.confirmed_at = confirmed_at

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at
