from datetime import timedelta
import pytest
from sqlalchemy.dialects import postgresql
from src.modules.journal.public.analysis import AnalysisConflictError, UserReprocessLimitError, reprocess_policy
from tests.unit.ai_processing.test_analysis_gateway import setup_gateway, NOW


@pytest.mark.asyncio
async def test_initial_submission_is_free_and_pending_repeat_does_not_charge():
    gateway, session, entry = setup_gateway()
    first = await gateway.submit("entry", "owner", now=NOW)
    second = await gateway.submit("entry", "owner", now=NOW)
    assert first["reprocess"]["user_used"] == second["reprocess"]["user_used"] == 0
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_three_user_requests_are_accepted_and_fourth_failed_retry_is_refused():
    gateway, session, entry = setup_gateway()
    entry.user_reprocess_count = 0
    entry.updated_at = NOW
    session.scalar.return_value = "failure"
    for number in range(1, 4):
        entry.status = "analysis_failed"
        revision = entry.updated_at
        accepted = await gateway.submit("entry", "owner", now=NOW + timedelta(seconds=number), expected_revision=revision)
        assert entry.user_reprocess_count == number
        assert accepted["reprocess"]["user_used"] == number
        assert accepted["reprocess"]["requires_admin"] is False  # still pending
        audit = session.add.call_args.args[0]
        assert audit.actor_role == "USER" and audit.requested_by == "owner"
        assert audit.user_attempt_number == number and audit.failure_id == "failure"
        await gateway.submit("entry", "owner", now=NOW, expected_revision=revision)
        assert entry.user_reprocess_count == number
    entry.status = "analysis_failed"
    assert reprocess_policy(entry)["requires_admin"] is True
    with pytest.raises(UserReprocessLimitError):
        await gateway.submit("entry", "owner", now=NOW, expected_revision=entry.updated_at)
    assert session.add.call_count == 3
    assert entry.status == "analysis_failed" and entry.user_reprocess_count == 3
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "FOR UPDATE" in str(query) and "owner" in query.params.values()


@pytest.mark.asyncio
@pytest.mark.parametrize("revision", [None, NOW - timedelta(seconds=1)])
async def test_stale_or_missing_revision_does_not_consume_user_retry(revision):
    gateway, session, entry = setup_gateway()
    entry.status = "analysis_failed"
    entry.user_reprocess_count = 1
    entry.updated_at = NOW
    with pytest.raises(AnalysisConflictError):
        await gateway.submit("entry", "owner", now=NOW, expected_revision=revision)
    assert entry.user_reprocess_count == 1
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_admin_can_retry_foreign_entry_after_limit_without_resetting_quota():
    gateway, session, entry = setup_gateway()
    entry.status = "analysis_failed"
    entry.user_reprocess_count = 3
    session.scalar.return_value = "failure"
    result = await gateway.admin_reprocess("failure", "admin", now=NOW)
    assert result["status"] == "pending_analysis" and result["already_pending"] is False
    assert entry.user_reprocess_count == 3
    audit = session.add.call_args.args[0]
    assert audit.actor_role == "ADMIN" and audit.requested_by == "admin"
    assert audit.user_attempt_number is None
    result = await gateway.admin_reprocess("failure", "admin", now=NOW)
    assert result["already_pending"] is True
    session.add.assert_called_once()
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "FOR UPDATE OF journal_entries" in str(query)
    assert "admin" not in query.params.values()  # not scoped to admin's own entries


@pytest.mark.asyncio
@pytest.mark.parametrize("state,latest", [("analyzed", "failure"), ("deleted", "failure"), ("analysis_failed", "newer-failure")])
async def test_admin_rejects_old_or_completed_failure(state, latest):
    gateway, session, entry = setup_gateway()
    entry.status = state
    session.scalar.return_value = latest
    with pytest.raises(AnalysisConflictError):
        await gateway.admin_reprocess("failure", "admin", now=NOW)
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_admin_rejects_missing_or_deleted_entry():
    from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
    gateway, session, _ = setup_gateway()
    session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(JournalEntryNotFoundError):
        await gateway.admin_reprocess("failure", "admin", now=NOW)
    session.add.assert_not_called()
