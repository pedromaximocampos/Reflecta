import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.ai_processing.application.contracts import InterpretationFailedError, ProviderNotConfiguredError
from src.modules.ai_processing.worker import process_one
from src.modules.journal.public.analysis import AnalysisConflictError, EntrySnapshot


def setup():
    snapshot = EntrySnapshot("entry", "owner", "Fictício", None, datetime.now(timezone.utc), "pending_analysis")
    gateway = SimpleNamespace(next_pending=AsyncMock(return_value=snapshot), mark_failed=AsyncMock())
    case = SimpleNamespace(execute=AsyncMock(return_value="analysis"))
    return gateway, case, snapshot


@pytest.mark.asyncio
async def test_worker_uses_database_owner_and_processes_selected_entry():
    gateway, case, _ = setup()
    assert await process_one(gateway, case, entry_id="entry")
    gateway.next_pending.assert_awaited_once_with("entry")
    case.execute.assert_awaited_once_with("entry", "owner")
    gateway.mark_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_queue_does_not_call_ai():
    gateway, case, _ = setup()
    gateway.next_pending.return_value = None
    assert not await process_one(gateway, case)
    case.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_failure_leaves_retry_explicit():
    gateway, case, snapshot = setup()
    case.execute.side_effect = InterpretationFailedError()
    await process_one(gateway, case)
    assert gateway.mark_failed.call_args.args == (snapshot,)


@pytest.mark.asyncio
async def test_conflict_does_not_overwrite_entry():
    gateway, case, _ = setup()
    case.execute.side_effect = AnalysisConflictError()
    await process_one(gateway, case)
    gateway.mark_failed.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [ProviderNotConfiguredError, asyncio.CancelledError])
async def test_configuration_and_cancellation_preserve_pending_entry(error):
    gateway, case, _ = setup()
    case.execute.side_effect = error()
    with pytest.raises(error):
        await process_one(gateway, case)
    gateway.mark_failed.assert_not_awaited()
