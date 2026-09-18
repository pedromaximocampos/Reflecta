from datetime import datetime, timezone

import pytest

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.exceptions.journal_exceptions import (
    EmptyJournalContentError,
    JournalEntryNotEditableError,
)
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId


NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 9, 18, 13, 0, tzinfo=timezone.utc)


def make_entry(status: JournalEntryStatus = JournalEntryStatus.DRAFT) -> JournalEntry:
    return JournalEntry(
        id=JournalEntryId("01JOURNAL00000000000000000"),
        user_id=UserId("01USER0000000000000000000"),
        title=" Meu dia ",
        content_text=" Uma reflexão importante. ",
        status=status,
        created_at=NOW,
    )


def test_creation_normalizes_title_and_content() -> None:
    entry = make_entry()

    assert entry.title == "Meu dia"
    assert entry.content_text == "Uma reflexão importante."


def test_creation_rejects_blank_content() -> None:
    with pytest.raises(EmptyJournalContentError):
        JournalEntry(
            id=JournalEntryId("01JOURNAL00000000000000000"),
            user_id=UserId("01USER0000000000000000000"),
            title=None,
            content_text="   ",
            status=JournalEntryStatus.DRAFT,
            created_at=NOW,
        )


def test_draft_can_update_and_clear_optional_fields() -> None:
    entry = make_entry()

    entry.update_title(None, now=LATER)
    entry.update_content(" Conteúdo atualizado. ", now=LATER)
    entry.update_context_tags(None, now=LATER)

    assert entry.title is None
    assert entry.content_text == "Conteúdo atualizado."
    assert entry.context_tags is None
    assert entry.updated_at == LATER


def test_non_draft_entry_cannot_be_edited() -> None:
    entry = make_entry(JournalEntryStatus.PENDING_ANALYSIS)

    with pytest.raises(JournalEntryNotEditableError):
        entry.update_content("Novo conteúdo", now=LATER)


def test_delete_marks_entry_as_logically_deleted() -> None:
    entry = make_entry()

    entry.delete(now=LATER)

    assert entry.status is JournalEntryStatus.DELETED
    assert entry.deleted_at == LATER
    assert entry.updated_at == LATER
