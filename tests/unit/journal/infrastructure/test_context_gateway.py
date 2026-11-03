from src.modules.journal.public.context_analysis import ContextPeriod
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects import postgresql
from src.modules.journal.infrastructure.persistence.postgresql.context_gateway import ContextGateway
from src.modules.ai_processing.application.contextual_analysis import HistoryChangedError, fingerprint


PERIOD = ContextPeriod(start_date="2026-10-20", end_date="2026-10-26")

def setup():
    session = AsyncMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    return ContextGateway(SimpleNamespace(session=lambda: manager)), session


@pytest.mark.asyncio
async def test_period_entries_filters_owner_and_deleted_rows_and_bounds_input():
    gateway, session = setup()
    now = datetime.now(timezone.utc)
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value.all.return_value = [SimpleNamespace(
        id="latest", content_text="Texto", context_tags=None, created_at=now, updated_at=None)]
    entries = await gateway.period_entries("owner", PERIOD)
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "user_id" in str(query)
    assert "deleted_at IS NULL" in str(query)
    assert "status !=" in str(query)
    assert "owner" in query.params.values()
    assert "LIMIT" not in str(query)
    assert PERIOD.bounds()[0] in query.params.values()
    assert PERIOD.bounds()[1] in query.params.values()
    assert entries[0]["id"] == "latest"


@pytest.mark.asyncio
async def test_cache_cannot_return_another_users_result():
    gateway, session = setup()
    session.scalar.return_value = None
    assert await gateway.find("owner", "key") is None
    query = session.scalar.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "owner" in query.params.values()
    assert "key" in query.params.values()
    assert "user_id" in str(query)


@pytest.mark.asyncio
async def test_changed_snapshot_is_never_inserted():
    gateway, session = setup()
    gateway.period_entries = AsyncMock(return_value=[])
    entries = [{"id": "deleted"}]
    with pytest.raises(HistoryChangedError):
        await gateway.save("owner", fingerprint(entries, PERIOD), entries, {}, PERIOD)
    assert session.execute.await_count == 1  # locks only; no insert


@pytest.mark.asyncio
async def test_duplicate_save_uses_unique_owner_snapshot_constraint():
    gateway, session = setup()
    entries = [{"id": "entry"}]
    gateway.period_entries = AsyncMock(return_value=entries)
    session.scalar.return_value = SimpleNamespace(id="saved", entry_ids=["entry"], result={},
                                                 created_at=datetime.now(timezone.utc), period_start=None, period_end=None)
    assert (await gateway.save("owner", fingerprint(entries, PERIOD), entries, {}, PERIOD))["id"] == "saved"
    statement = session.execute.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    assert "ON CONFLICT ON CONSTRAINT uq_context_user_snapshot DO NOTHING" in str(statement)
    assert statement.params["user_id"] == "owner"


@pytest.mark.asyncio
async def test_history_is_paginated_owner_scoped_and_hides_deleted_source_content():
    gateway, session = setup()
    now = datetime.now(timezone.utc)
    rows = [SimpleNamespace(id="latest", entry_ids=["a", "b"], result={"summary": "Visible"}, created_at=now, period_start=None, period_end=None),
            SimpleNamespace(id="old", entry_ids=["a", "deleted"], result={"summary": "Private deleted text"}, created_at=now, period_start=None, period_end=None)]
    session.scalar.return_value = 9
    analyses = MagicMock()
    analyses.scalars.return_value.all.return_value = rows
    sources = MagicMock()
    sources.scalars.return_value.all.return_value = ["a", "b"]
    session.execute.side_effect = [analyses, sources]
    response = await gateway.history("owner", limit=2, offset=4)
    assert response["total"] == 9
    assert response["limit"] == 2
    assert response["offset"] == 4
    assert response["analyses"][0]["available"] is True
    assert response["analyses"][0]["result"] == {"summary": "Visible"}
    hidden = response["analyses"][1]
    assert hidden["available"] is False
    assert hidden["result"] is None
    assert hidden["entry_ids"] == []
    assert hidden["entry_count"] == 2
    for call in [session.scalar.call_args, *session.execute.call_args_list]:
        query = call.args[0].compile(dialect=postgresql.dialect())
        assert "owner" in query.params.values()
    page_query = session.execute.call_args_list[0].args[0].compile(dialect=postgresql.dialect())
    assert "created_at DESC" in str(page_query) and "id DESC" in str(page_query)
    assert 2 in page_query.params.values() and 4 in page_query.params.values()


@pytest.mark.asyncio
async def test_empty_history_does_not_query_source_records():
    gateway, session = setup()
    session.scalar.return_value = 0
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value.all.return_value = []
    assert await gateway.history("owner") == {"analyses": [], "total": 0, "limit": 5, "offset": 0}
    session.execute.assert_awaited_once()
