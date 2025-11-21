from src.domain.ports.system.iclock import IClock
from datetime import datetime, timezone
from src.core.settings import get_settings

_settings = get_settings()

class SystemClock(IClock):

    def access_token_expiration_in_seconds(self) -> int:
        return _settings.access_token_minutes * 60

    def refresh_token_expiration_in_seconds(self) -> int:
        return _settings.refresh_token_days * 24 * 60 * 60

    def now(self) -> datetime:
        return datetime.now(timezone.utc)