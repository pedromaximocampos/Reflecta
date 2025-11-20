from src.domain.ports.system.iclock import IClock
from datetime import datetime, timezone
from typing import Final

class SystemClock(IClock):
    _ACCESS_TOKEN_EXPIRES_IN_SECONDS: Final[int] = 15 * 60  # 15 minutos

    _REFRESH_TOKEN_EXPIRES_IN_SECONDS: Final[int] = 30 * 24 * 60 * 60  # 30 dias

    def access_token_expiration_in_seconds(self) -> int:
        return self._ACCESS_TOKEN_EXPIRES_IN_SECONDS

    def refresh_token_expiration_in_seconds(self) -> int:
        return self._REFRESH_TOKEN_EXPIRES_IN_SECONDS

    def now(self) -> datetime:
        return datetime.now(timezone.utc)