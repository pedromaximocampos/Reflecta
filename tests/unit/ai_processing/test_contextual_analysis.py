from src.modules.journal.public.context_analysis import ContextPeriod
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.modules.ai_processing.application.contextual_analysis import (
    AnalyzeContext, InsufficientHistoryError, HistoryChangedError, fingerprint,
)
from src.modules.ai_processing.application.contracts import InterpretationFailedError


PERIOD = ContextPeriod(start_date="2026-10-20", end_date="2026-10-26")

def setup(count=5):
    entries = [{"id": str(i), "content_text": "Reflexão", "created_at": str(i)} for i in range(count)]
    gateway = SimpleNamespace(period_entries=AsyncMock(return_value=entries),
        find=AsyncMock(return_value=None), save=AsyncMock(return_value={"id": "saved"}))
    provider = SimpleNamespace(respond=AsyncMock(return_value={"summary": "Síntese do período",
        "recurring_patterns": ["Trabalho recorrente"], "changes_over_time": [], "reflection_questions": []}))
    return AnalyzeContext(gateway, provider), gateway, provider, entries


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 1, 4])
async def test_minimum_is_enforced_before_provider_or_save(count):
    case, gateway, provider, _ = setup(count)
    with pytest.raises(InsufficientHistoryError):
        await case.execute("owner", PERIOD)
    gateway.period_entries.assert_awaited_once_with("owner", PERIOD)
    gateway.find.assert_not_awaited()
    provider.respond.assert_not_awaited()
    gateway.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_request_analyzes_five_entries_and_scopes_save_to_owner():
    case, gateway, provider, entries = setup()
    assert await case.execute("owner", PERIOD) == {"id": "saved"}
    assert provider.respond.call_args.kwargs["input_data"] == {"period": PERIOD.describe(), "entries": entries}
    gateway.find.assert_awaited_once_with("owner", fingerprint(entries, PERIOD))
    gateway.save.assert_awaited_once_with("owner", fingerprint(entries, PERIOD), entries, provider.respond.return_value, PERIOD)


@pytest.mark.asyncio
async def test_same_snapshot_reuses_saved_result_without_paid_request():
    case, gateway, provider, _ = setup()
    gateway.find.return_value = {"id": "existing"}
    assert await case.execute("owner", PERIOD) == {"id": "existing"}
    provider.respond.assert_not_awaited()
    gateway.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_unavailable_provider_does_not_replace_saved_history():
    case, gateway, provider, _ = setup()
    provider.respond.side_effect = InterpretationFailedError("sensitive provider error")
    with pytest.raises(InterpretationFailedError):
        await case.execute("owner", PERIOD)
    gateway.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_provider_output_is_not_saved():
    case, gateway, provider, _ = setup()
    provider.respond.return_value = {"summary": " "}
    with pytest.raises(ValidationError):
        await case.execute("owner", PERIOD)
    gateway.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_deleted_or_changed_sources_reject_result():
    case, gateway, _, _ = setup()
    gateway.save.side_effect = HistoryChangedError()
    with pytest.raises(HistoryChangedError):
        await case.execute("owner", PERIOD)


def test_snapshot_changes_for_edits_new_entries_and_deletions():
    _, _, _, entries = setup()
    original = fingerprint(entries)
    assert fingerprint(entries[:-1]) != original
    assert fingerprint(entries + [{"id": "new"}]) != original
    assert fingerprint([{**entries[0], "content_text": "Editado"}, *entries[1:]]) != original


@pytest.mark.asyncio
@pytest.mark.parametrize('count', [5, 6, 12])
async def test_every_entry_in_period_is_sent_not_just_five_or_seven(count):
    case, gateway, provider, entries = setup(count)
    await case.execute('owner', PERIOD)
    assert provider.respond.call_args.kwargs['input_data']['entries'] == entries


def test_cache_key_includes_period_even_when_entry_set_is_identical():
    _, _, _, entries = setup()
    other = ContextPeriod(start_date='2026-10-21', end_date='2026-10-27')
    assert fingerprint(entries, PERIOD) != fingerprint(entries, other)
