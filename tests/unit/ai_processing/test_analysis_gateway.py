from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects import postgresql

from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
from src.modules.journal.public.analysis import AnalysisConflictError
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def setup_gateway():
    entry = JournalEntryModel(id="entry", user_id="owner", content_text="Texto",
                              status="draft", created_at=NOW, updated_at=None, context_tags=None)
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=entry))
    session.scalar.return_value = None
    db = MagicMock()
    db.session.return_value.__aenter__ = AsyncMock(return_value=session)
    db.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return JournalAnalysisGateway(db), session, entry


async def save(gateway, snapshot):
    await gateway.save(snapshot, analysis_id="analysis", summary="Resumo", main_message="Mensagem",
                       metadata={"themes": []}, now=NOW)


@pytest.mark.asyncio
async def test_read_is_scoped_to_owner_and_non_deleted_entry():
    gateway, session, _ = setup_gateway()
    snapshot = await gateway.read("entry", "owner")
    compiled = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "journal_entries.user_id =" in str(compiled)
    assert "deleted_at IS NULL" in str(compiled)
    assert "owner" in compiled.params.values()
    assert snapshot.user_id == "owner"


@pytest.mark.asyncio
async def test_save_locks_entry_and_writes_analysis_and_status_together():
    gateway, session, entry = setup_gateway()
    await save(gateway, gateway._snapshot(entry))
    statement = str(session.execute.call_args.args[0].compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE" in statement
    model = session.add.call_args.args[0]
    assert model.journal_entry_id == "entry"
    assert model.status == "completed"
    assert model.analysis_error is None
    assert entry.status == "analyzed"
    assert entry.updated_at == NOW


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["content", "status", "timestamp", "completed", "deleted"])
async def test_stale_deleted_or_completed_result_never_adds_analysis(change):
    gateway, session, entry = setup_gateway()
    snapshot = gateway._snapshot(entry)
    expected = AnalysisConflictError
    if change == "content":
        entry.content_text = "Editado"
    elif change == "status":
        entry.status = "analyzed"
    elif change == "timestamp":
        entry.updated_at = NOW
    elif change == "completed":
        session.scalar.return_value = "existing-analysis"
    else:
        session.execute.return_value.scalar_one_or_none.return_value = None
        expected = JournalEntryNotFoundError
    with pytest.raises(expected):
        await save(gateway, snapshot)
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_repeated_save_does_not_duplicate_analysis():
    gateway, session, entry = setup_gateway()
    snapshot = gateway._snapshot(entry)
    await save(gateway, snapshot)
    with pytest.raises(AnalysisConflictError):
        await save(gateway, snapshot)
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_commit_failure_rolls_back_analysis_and_entry_transaction():
    _, session, entry = setup_gateway()
    session.__aenter__.return_value = session
    session.commit.side_effect = RuntimeError("database unavailable")
    db = object.__new__(DBConnectionHandler)
    db._session_factory = MagicMock(return_value=session)
    gateway = JournalAnalysisGateway(db)
    with pytest.raises(RuntimeError):
        await save(gateway, gateway._snapshot(entry))
    session.commit.assert_awaited_once()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_transitions_draft_and_is_idempotent_for_pending():
    gateway, _, entry = setup_gateway()
    await gateway.submit("entry", "owner", now=NOW)
    assert entry.status == "pending_analysis"
    assert entry.updated_at == NOW
    await gateway.submit("entry", "owner", now=NOW)
    assert entry.status == "pending_analysis"


@pytest.mark.asyncio
async def test_submit_rejects_analyzed_entry():
    gateway, _, entry = setup_gateway()
    entry.status = "analyzed"
    with pytest.raises(AnalysisConflictError):
        await gateway.submit("entry", "owner", now=NOW)


@pytest.mark.asyncio
async def test_pending_query_excludes_drafts_and_deleted_entries():
    gateway, session, _ = setup_gateway()
    await gateway.next_pending("entry")
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "pending_analysis" in query.params.values()
    assert "entry" in query.params.values()
    assert "deleted_at IS NULL" in str(query)


@pytest.mark.asyncio
async def test_failed_update_is_scoped_and_checks_snapshot():
    gateway, session, entry = setup_gateway()
    await gateway.mark_failed(gateway._snapshot(entry), now=NOW)
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "updated_at IS NULL" in str(query)
    assert "deleted_at IS NULL" in str(query)
    assert "owner" in query.params.values()
    assert "pending_analysis" in query.params.values()
    assert "analysis_failed" in query.params.values()


@pytest.mark.asyncio
async def test_analysis_lookup_hides_other_users_or_deleted_entries():
    gateway, session, _ = setup_gateway()
    session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(JournalEntryNotFoundError):
        await gateway.get_analysis("entry", "other-user")
    session.execute.assert_awaited_once()
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "other-user" in query.params.values()
    assert "deleted_at IS NULL" in str(query)


@pytest.mark.asyncio
async def test_analysis_lookup_returns_status_when_no_result_exists():
    gateway, session, entry = setup_gateway()
    entry.status = "pending_analysis"
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
    ]
    assert await gateway.get_analysis("entry", "owner") == {
        "entry_id": "entry", "status": "pending_analysis", "analysis": None,
    }


@pytest.mark.asyncio
async def test_analysis_lookup_returns_completed_content_and_metadata():
    from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
    gateway, session, entry = setup_gateway()
    entry.status = "analyzed"
    result = AnalysisModel(id="analysis", summary="Resumo", main_message="Mensagem",
                           content_meta={"sentiments": ["calma"]}, analyzed_at=NOW)
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=result)),
    ]
    output = await gateway.get_analysis("entry", "owner")
    assert output["analysis"]["summary"] == "Resumo"
    assert output["analysis"]["metadata"] == {"sentiments": ["calma"]}
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "completed" in query.params.values()
    assert "entry" in query.params.values()
