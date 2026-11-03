import hashlib
import json
from typing import Protocol

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, model_validator

MIN_ENTRIES = 5
PERIOD_TIMEZONE = "America/Sao_Paulo"


class ContextPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def exactly_seven_days(self):
        if (self.end_date - self.start_date).days != 6 or self.end_date == date.max:
            raise ValueError("O período deve conter exatamente 7 dias, incluindo início e fim.")
        return self

    def bounds(self):
        zone = ZoneInfo(PERIOD_TIMEZONE)
        return (datetime.combine(self.start_date, time.min, zone).astimezone(timezone.utc),
                datetime.combine(self.end_date + timedelta(days=1), time.min, zone).astimezone(timezone.utc))

    def describe(self):
        return {**self.model_dump(mode="json"), "timezone": PERIOD_TIMEZONE}



class InsufficientHistoryError(Exception):
    pass


class HistoryChangedError(Exception):
    pass


def fingerprint(entries, period=None):
    snapshot = {"period": period.describe(), "entries": entries} if period else entries
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class IContextGateway(Protocol):
    async def period_entries(self, user_id: str, period: ContextPeriod) -> list[dict]: ...
    async def find(self, user_id: str, key: str) -> dict | None: ...
    async def save(self, user_id: str, key: str, entries: list[dict], result: dict, period: ContextPeriod) -> dict: ...
