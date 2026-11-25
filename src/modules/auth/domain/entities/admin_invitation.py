from dataclasses import dataclass
from datetime import datetime

from src.modules.auth.public.user_id import UserId


@dataclass(slots=True)
class AdminInvitation:
    id: str
    target_user_id: UserId
    invited_by_user_id: UserId
    target_email: str
    target_username: str
    token_hash: str
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None

    @property
    def is_accepted(self) -> bool:
        return self.accepted_at is not None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at <= now

    def status_at(self, now: datetime) -> str:
        if self.is_accepted:
            return "ACCEPTED"
        if self.is_revoked:
            return "REVOKED"
        if self.is_expired(now):
            return "EXPIRED"
        return "PENDING"

    def accept(self, accepted_at: datetime) -> None:
        self.accepted_at = accepted_at

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at
