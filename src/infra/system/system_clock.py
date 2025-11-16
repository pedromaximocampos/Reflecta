from src.domain.ports.system.iclock import IClock
from datetime import datetime, timezone


class SystemClock(IClock):

    def now(self) -> datetime:
        return datetime.now(timezone.utc)