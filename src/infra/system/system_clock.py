from src.domain.ports.system.iclock import IClock
from datetime import datetime, timezone


class SystemClock(IClock):

    def access_token_expiration(self) -> int:
        pass

    def refresh_token_expiration(self) -> int:
        pass

    def now(self) -> datetime:
        return datetime.now(timezone.utc)