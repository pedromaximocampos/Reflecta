from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects import postgresql

from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
from src.modules.journal.public.analysis import AnalysisConflictError, AnalysisFailure
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
                       metadata={"themes": []}, now=NOW, sentences=())


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
    await gateway.mark_failed(gateway._snapshot(entry), now=NOW, failure=AnalysisFailure("provider_timeout", "Tempo limite excedido.", 1))
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
        "reprocess": {"user_limit": 3, "user_used": 0, "user_remaining": 3,
                      "can_user_reprocess": False, "requires_admin": False, "revision": NOW.isoformat()},
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
        MagicMock(all=MagicMock(return_value=[])),
    ]
    output = await gateway.get_analysis("entry", "owner")
    assert output["analysis"]["summary"] == "Resumo"
    assert output["analysis"]["metadata"] == {"sentiments": ["calma"]}
    assert output["analysis"]["sentences"] == []
    query = session.execute.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    assert "completed" in query.params.values()
    assert "entry" in query.params.values()


@pytest.mark.asyncio
async def test_save_includes_sentences_and_theme_associations_in_same_transaction():
    from src.modules.journal.public.analysis import SentenceAnalysis, SentencePassageAnalysis
    from src.modules.journal.infrastructure.persistence.postgresql.models.journal_sentence_model import JournalSentenceModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_passage_model import SentencePassageModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_theme_model import SentenceThemeModel
    gateway, session, entry = setup_gateway()
    sentences = (SentenceAnalysis("sentence", 0, "Texto", 0, 5, ({
        "id": "theme", "slug": "trabalho", "confidence": 0.75,
    },), (SentencePassageAnalysis(
        id="sentence-passage",
        passage_id="passage",
        confidence=0.91,
        reason="A relação foi explicada.",
        payload_snapshot={"schema_version": 1, "short_text": "Passagem."},
    ),)),)
    await gateway.save(gateway._snapshot(entry), analysis_id="analysis", summary="Resumo",
                       main_message="Mensagem", metadata={}, now=NOW, sentences=sentences)
    models = [call.args[0] for call in session.add.call_args_list]
    sentence = next(model for model in models if isinstance(model, JournalSentenceModel))
    theme = next(model for model in models if isinstance(model, SentenceThemeModel))
    passage = next(model for model in models if isinstance(model, SentencePassageModel))
    assert (sentence.journal_entry_id, sentence.analysis_id, sentence.sentence_text) == ("entry", "analysis", "Texto")
    assert (sentence.start_offset, sentence.end_offset) == (0, 5)
    assert (theme.sentence_id, theme.theme_id, theme.theme_slug, theme.confidence) == ("sentence", "theme", "trabalho", 0.75)
    assert theme.source == "ai" and theme.confirmed_by_user is False
    assert (passage.id, passage.sentence_id, passage.passage_id) == (
        "sentence-passage", "sentence", "passage",
    )
    assert passage.confidence == Decimal("0.91")
    assert passage.reason == "A relação foi explicada."
    assert passage.payload_snapshot == {
        "schema_version": 1,
        "short_text": "Passagem.",
    }
    assert entry.status == "analyzed"
    assert session.flush.await_count == 2


@pytest.mark.asyncio
async def test_analysis_returns_ordered_sentences_including_sentences_without_themes():
    from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.journal_sentence_model import JournalSentenceModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_passage_model import SentencePassageModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_theme_model import SentenceThemeModel
    gateway, session, entry = setup_gateway()
    result = AnalysisModel(id="analysis", content_meta={"themes": [{"id": "theme", "label": "Trabalho"}]})
    first = JournalSentenceModel(id="s1", sentence_index=0, sentence_text="Texto.", start_offset=0, end_offset=6)
    second = JournalSentenceModel(id="s2", sentence_index=1, sentence_text="Outro.", start_offset=7, end_offset=13)
    match = SentenceThemeModel(theme_id="theme", theme_slug="trabalho", confidence=Decimal("0.7500"),
                               source="ai", confirmed_by_user=False)
    passage = SentencePassageModel(
        id="sp1",
        sentence_id="s1",
        passage_id="passage-1",
        confidence=Decimal("0.9100"),
        reason="A passagem amplia a perspectiva da frase.",
        payload_snapshot={
            "schema_version": 1,
            "short_text": "Passagem canônica.",
            "work": {"title": "Obra", "author_name": "Autoria"},
        },
        created_at=NOW,
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=result)),
        MagicMock(all=MagicMock(return_value=[(first, match), (second, None)])),
        MagicMock(scalars=MagicMock(return_value=MagicMock(
            all=MagicMock(return_value=[passage]),
        ))),
    ]
    output = await gateway.get_analysis("entry", "owner")
    sentences = output["analysis"]["sentences"]
    assert [s["sentence_text"] for s in sentences] == ["Texto.", "Outro."]
    assert sentences[0]["themes"] == [{"id": "theme", "label": "Trabalho", "slug": "trabalho",
                                       "confidence": 0.75, "source": "ai", "confirmed_by_user": False}]
    assert sentences[1]["themes"] == []
    assert sentences[0]["passages"] == [{
        "id": "sp1",
        "passage_id": "passage-1",
        "confidence": 0.91,
        "reason": "A passagem amplia a perspectiva da frase.",
        "payload_snapshot": {
            "schema_version": 1,
            "short_text": "Passagem canônica.",
            "work": {"title": "Obra", "author_name": "Autoria"},
        },
    }]
    assert sentences[1]["passages"] == []


@pytest.mark.asyncio
async def test_failed_attempt_persists_safe_diagnosis_and_keeps_completed_lookup_separate():
    import json
    gateway, session, entry = setup_gateway()
    failure = AnalysisFailure("provider_timeout", "Tempo limite excedido.", 2)
    await gateway.mark_failed(gateway._snapshot(entry), now=NOW, failure=failure)
    model = session.add.call_args.args[0]
    assert model.status == "failed"
    assert model.journal_entry_id == entry.id
    assert model.analyzed_at is None
    assert model.summary is None and model.main_message is None
    assert json.loads(model.analysis_error) == {
        "code": failure.code, "message": failure.message, "attempts": 2,
    }
    assert "RETURNING" in str(session.execute.call_args.args[0])


@pytest.mark.asyncio
async def test_stale_failure_does_not_create_failure_history():
    gateway, session, entry = setup_gateway()
    session.execute.return_value.scalar_one_or_none.return_value = None
    await gateway.mark_failed(gateway._snapshot(entry), now=NOW,
                              failure=AnalysisFailure("unexpected_error", "Falha interna.", 1))
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_failure_record_and_transition_roll_back_if_commit_fails():
    _, session, entry = setup_gateway()
    session.__aenter__.return_value = session
    session.commit.side_effect = RuntimeError("database unavailable")
    db = object.__new__(DBConnectionHandler)
    db._session_factory = MagicMock(return_value=session)
    gateway = JournalAnalysisGateway(db)
    with pytest.raises(RuntimeError):
        await gateway.mark_failed(gateway._snapshot(entry), now=NOW,
                                  failure=AnalysisFailure("unexpected_error", "Falha interna.", 1))
    session.add.assert_called_once()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_failure_history_is_scoped_to_owner_and_excludes_deleted_entries():
    gateway, session, _ = setup_gateway()
    session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(JournalEntryNotFoundError):
        await gateway.get_analysis_failures('entry', 'other-owner')
    session.execute.assert_awaited_once()
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert 'other-owner' in query.params.values()
    assert 'deleted_at IS NULL' in str(query)


@pytest.mark.asyncio
async def test_failure_history_returns_diagnosis_and_retry_eligibility():
    from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
    gateway, session, entry = setup_gateway()
    entry.status = 'analysis_failed'
    failure = AnalysisModel(id='failure', created_at=NOW, analysis_error='{"code":"provider_timeout","message":"Tempo limite excedido.","attempts":1}')
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[failure])))),
    ]
    result = await gateway.get_analysis_failures('entry', 'owner', limit=5)
    assert result == {'entry_id': 'entry', 'status': 'analysis_failed', 'can_reprocess': True, 'failures': [
        {'id': 'failure', 'code': 'provider_timeout', 'message': 'O provedor excedeu o tempo limite da análise.', 'attempts': 1, 'failed_at': NOW.isoformat()},
    ]}
    query = session.execute.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    assert 'failed' in query.params.values() and 5 in query.params.values()
    assert 'ORDER BY' in str(query)


@pytest.mark.asyncio
@pytest.mark.parametrize('raw', [None, 'secret raw exception', 'null', '[]', '{}', '{"code":"x","message":"secret","attempts":true}'])
async def test_legacy_failure_never_exposes_raw_error(raw):
    from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
    gateway, session, entry = setup_gateway()
    entry.status = 'analyzed'
    failure = AnalysisModel(id='failure', created_at=NOW, analysis_error=raw)
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[failure])))),
    ]
    result = await gateway.get_analysis_failures('entry', 'owner')
    assert result['can_reprocess'] is False
    assert result['failures'][0]['code'] == 'unknown_error'
    assert 'secret' not in str(result)


@pytest.mark.asyncio
async def test_old_failed_entry_without_diagnostic_returns_empty_history():
    gateway, session, entry = setup_gateway()
    entry.status = 'analysis_failed'
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=entry)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    result = await gateway.get_analysis_failures('entry', 'owner')
    assert result == {'entry_id':'entry', 'status':'analysis_failed', 'can_reprocess':True, 'failures':[]}
