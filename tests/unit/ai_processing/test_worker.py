import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.ai_processing.application.contracts import InterpretationFailedError, ProviderNotConfiguredError, InvalidInterpretationError
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
async def test_worker_reuses_same_provider_scope_for_complete_analysis():
    gateway, case, _ = setup()
    lifecycle = []

    class Provider:
        @asynccontextmanager
        async def request_scope(self):
            lifecycle.append("entered")
            try:
                yield
            finally:
                lifecycle.append("closed")

    provider = Provider()
    case.interpreter = provider
    case.passage_selector = provider

    await process_one(gateway, case)

    assert lifecycle == ["entered", "closed"]
    case.execute.assert_awaited_once_with("entry", "owner")


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
async def test_invalid_result_retries_once_and_recovers():
    gateway, case, _ = setup()
    case.execute.side_effect = [InvalidInterpretationError(), "analysis"]
    await process_one(gateway, case)
    assert case.execute.await_count == 2
    gateway.mark_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_repeated_invalid_result_marks_failed_without_infinite_retries():
    gateway, case, snapshot = setup()
    case.execute.side_effect = InvalidInterpretationError()
    await process_one(gateway, case)
    assert case.execute.await_count == 2
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


@pytest.mark.asyncio
async def test_worker_records_allowlisted_reason_not_exception_text():
    from src.modules.ai_processing.application.failure_reasons import FailureReason
    gateway, case, _ = setup()
    case.execute.side_effect = InterpretationFailedError("secret journal and key", reason=FailureReason.QUOTA)
    await process_one(gateway, case)
    failure = gateway.mark_failed.call_args.kwargs["failure"]
    assert failure.code == "provider_quota_exceeded"
    assert failure.message == FailureReason.QUOTA.message
    assert failure.attempts == 1
    assert "secret" not in failure.message


@pytest.mark.asyncio
async def test_unknown_errors_do_not_persist_arbitrary_exception_messages():
    gateway, case, _ = setup()
    case.execute.side_effect = RuntimeError("secret journal and key")
    await process_one(gateway, case)
    failure = gateway.mark_failed.call_args.kwargs["failure"]
    assert failure.code == "unexpected_error"
    assert "secret" not in failure.message


@pytest.mark.asyncio
async def test_invalid_result_records_two_attempts_after_bounded_retry():
    gateway, case, _ = setup()
    case.execute.side_effect = InvalidInterpretationError("sensitive invalid result")
    await process_one(gateway, case)
    failure = gateway.mark_failed.call_args.kwargs["failure"]
    assert failure.code == "invalid_interpretation"
    assert failure.attempts == 2
