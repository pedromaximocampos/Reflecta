from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import (
    UserModel,
)
from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.infrastructure.persistence.postgresql.mappers.journal_entry_mapper import (
    JournalEntryMapper,
)
from src.modules.journal.infrastructure.persistence.postgresql.models import (
    AnalysisModel,
    EntryEmbeddingModel,
    JournalEntryModel,
    JournalSentenceModel,
    SentenceEmbeddingModel,
    SentencePassageModel,
    SentenceThemeModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.repositories.journal_entry_repository import (
    JournalEntryRepository,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.infrastructure.persistence.postgresql.configs.base import Base


NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
ENTRY_ID = JournalEntryId("01JOURNAL00000000000000000")
USER_ID = UserId("01USER0000000000000000000")


def make_entry() -> JournalEntry:
    return JournalEntry(
        id=ENTRY_ID,
        user_id=USER_ID,
        title="Meu dia",
        content_text="Uma reflexão.",
        context_tags={"domains": []},
        status=JournalEntryStatus.DRAFT,
        created_at=NOW,
    )


def test_all_documented_journal_tables_use_journal_schema() -> None:
    assert UserModel.__table__.schema is None
    assert {
        AnalysisModel.__table__.fullname,
        EntryEmbeddingModel.__table__.fullname,
        JournalEntryModel.__table__.fullname,
        JournalSentenceModel.__table__.fullname,
        SentenceEmbeddingModel.__table__.fullname,
        SentencePassageModel.__table__.fullname,
        SentenceThemeModel.__table__.fullname,
    } == {
        "journal_schema.analysis",
        "journal_schema.entry_embeddings",
        "journal_schema.journal_entries",
        "journal_schema.journal_sentences",
        "journal_schema.sentence_embeddings",
        "journal_schema.sentence_passages",
        "journal_schema.sentence_themes",
    }
    assert "journal_schema.journal_entries" in Base.metadata.tables


def test_journal_entry_mapper_round_trip_preserves_domain_data() -> None:
    mapper = JournalEntryMapper()
    original = make_entry()

    mapped = mapper.to_entity(mapper.to_model(original))

    assert mapped.id == original.id
    assert mapped.user_id == original.user_id
    assert mapped.title == original.title
    assert mapped.content_text == original.content_text
    assert mapped.context_tags == original.context_tags
    assert mapped.status is JournalEntryStatus.DRAFT


@pytest.mark.asyncio
async def test_repository_find_by_id_is_scoped_by_owner_and_active_state() -> None:
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result
    repository = JournalEntryRepository(session, JournalEntryMapper())

    found = await repository.find_by_id_for_user(ENTRY_ID, USER_ID)

    statement = session.execute.await_args.args[0]
    compiled = statement.compile()
    assert found is None
    assert ENTRY_ID.value in compiled.params.values()
    assert USER_ID.value in compiled.params.values()
    assert "deleted_at IS NULL" in str(statement)


@pytest.mark.asyncio
async def test_repository_create_executes_insert_and_returns_entity() -> None:
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one.return_value = JournalEntryMapper().to_model(make_entry())
    session.execute.return_value = result
    repository = JournalEntryRepository(session, JournalEntryMapper())

    created = await repository.create(make_entry())

    statement = session.execute.await_args.args[0]
    assert statement.is_insert
    assert created.id == ENTRY_ID


@pytest.mark.asyncio
async def test_repository_rejects_unknown_update_fields() -> None:
    repository = JournalEntryRepository(AsyncMock(), JournalEntryMapper())

    with pytest.raises(ValueError, match="Invalid journal fields"):
        await repository.update(make_entry(), frozenset({"status"}))
