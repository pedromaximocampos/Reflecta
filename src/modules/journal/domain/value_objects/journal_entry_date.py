from datetime import date, datetime
from zoneinfo import ZoneInfo


JOURNAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def journal_date_at(instant: datetime) -> date:
    if instant.tzinfo is None:
        raise ValueError("Journal clock must return a timezone-aware instant.")
    return instant.astimezone(JOURNAL_TIMEZONE).date()
