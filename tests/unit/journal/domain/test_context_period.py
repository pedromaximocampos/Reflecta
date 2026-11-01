from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from src.modules.journal.public.context_analysis import ContextPeriod


@pytest.mark.parametrize('end', ['2026-10-19', '2026-10-20', '2026-10-25', '2026-10-27', '2026-11-01'])
def test_period_cannot_be_shorter_or_longer_than_seven_days(end):
    with pytest.raises(ValidationError):
        ContextPeriod(start_date='2026-10-20', end_date=end)


def test_period_covers_local_midnight_through_next_midnight_exclusive():
    period = ContextPeriod(start_date='2026-10-20', end_date='2026-10-26')
    start, stop = period.bounds()
    assert start == datetime(2026, 10, 20, 3, tzinfo=timezone.utc)
    assert stop == datetime(2026, 10, 27, 3, tzinfo=timezone.utc)


def test_seven_calendar_days_can_cross_month_and_leap_day():
    period = ContextPeriod(start_date='2024-02-26', end_date='2024-03-03')
    assert period.describe()['end_date'] == '2024-03-03'
