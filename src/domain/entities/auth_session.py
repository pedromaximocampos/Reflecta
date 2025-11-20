from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Optional

@dataclass(eq=False, slots=True)
class AuthSession:
    id: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    refresh_jti_hash: str
    updated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and datetime.now(timezone.utc) < self.expires_at

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at