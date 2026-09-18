from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.create_entry.create_journal_entry_use_case_impl import (
    CreateJournalEntryUseCaseImpl,
)
from src.modules.journal.application.use_cases.create_entry.dto import (
    CreateJournalEntryDTO,
)
from src.modules.journal.application.use_cases.delete_entry.delete_journal_entry_use_case import (
    DeleteJournalEntryUseCase,
)
from src.modules.journal.application.use_cases.delete_entry.dto import (
    DeleteJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.get_entry.dto import (
    GetJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.get_entry.get_journal_entry_use_case import (
    GetJournalEntryUseCase,
)
from src.modules.journal.application.use_cases.list_entries.dto import (
    ListJournalEntriesInputDTO,
)
from src.modules.journal.application.use_cases.list_entries.list_journal_entries_use_case import (
    ListJournalEntriesUseCase,
)
from src.modules.journal.application.use_cases.update_entry.dto import (
    UpdateJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.update_entry.update_journal_entry_use_case import (
    UpdateJournalEntryUseCase,
)
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.exceptions.journal_exceptions import (
    EmptyJournalUpdateError,
    JournalEntryNotEditableError,
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId


NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 9, 18, 13, 0, tzinfo=timezone.utc)
USER_ID = UserId("01USER0000000000000000000")
ENTRY_ID = JournalEntryId("01JOURNAL00000000000000000")


class FixedClock:
    def now(self) -> datetime:
        return LATER


class FixedUlidGenerator:
    def generate_ulid(self) -> str:
        return ENTRY_ID.value


class FakeJournalUnitOfWork:
    def __init__(self) -> None:
        self.journal_entry_repository = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.enter_count = 0

    async def __aenter__(self):
        self.enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()


def make_entry(status: JournalEntryStatus = JournalEntryStatus.DRAFT) -> JournalEntry:
    return JournalEntry(
        id=ENTRY_ID,
        user_id=USER_ID,
        title="Meu dia",
        content_text="Uma reflexão importante.",
        context_tags=None,
        status=status,
        created_at=NOW,
    )


@pytest.mark.asyncio
async def test_create_entry_persists_authenticated_owner_and_commits() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.create.side_effect = lambda entry: entry
    use_case = CreateJournalEntryUseCaseImpl(uow, FixedClock(), FixedUlidGenerator())

    output = await use_case.execute(
        CreateJournalEntryDTO(
            user_id=USER_ID,
            title="Meu dia",
            content_text="Uma reflexão importante.",
        )
    )

    persisted = uow.journal_entry_repository.create.await_args.args[0]
    assert persisted.id == ENTRY_ID
    assert persisted.user_id == USER_ID
    assert persisted.status is JournalEntryStatus.DRAFT
    assert output.id == ENTRY_ID
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_entry_scopes_query_to_authenticated_owner() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.find_by_id_for_user.return_value = make_entry()

    output = await GetJournalEntryUseCase(uow).execute(
        GetJournalEntryInputDTO(ENTRY_ID, USER_ID)
    )

    assert output.id == ENTRY_ID
    uow.journal_entry_repository.find_by_id_for_user.assert_awaited_once_with(
        ENTRY_ID,
        USER_ID,
    )
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_entry_returns_not_found_for_missing_or_foreign_entry() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.find_by_id_for_user.return_value = None

    with pytest.raises(JournalEntryNotFoundError):
        await GetJournalEntryUseCase(uow).execute(
            GetJournalEntryInputDTO(ENTRY_ID, USER_ID)
        )

    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_list_entries_uses_owner_and_pagination() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.list_by_user.return_value = [make_entry()]

    output = await ListJournalEntriesUseCase(uow).execute(
        ListJournalEntriesInputDTO(USER_ID, limit=20, offset=40)
    )

    assert len(output.entries) == 1
    uow.journal_entry_repository.list_by_user.assert_awaited_once_with(
        USER_ID,
        limit=20,
        offset=40,
    )


@pytest.mark.asyncio
async def test_update_entry_updates_only_requested_fields_and_commits() -> None:
    uow = FakeJournalUnitOfWork()
    entry = make_entry()
    uow.journal_entry_repository.find_by_id_for_user.return_value = entry
    uow.journal_entry_repository.update.side_effect = lambda entity, _: entity

    output = await UpdateJournalEntryUseCase(uow, FixedClock()).execute(
        UpdateJournalEntryInputDTO(
            journal_entry_id=ENTRY_ID,
            user_id=USER_ID,
            content_text="Conteúdo atualizado.",
            fields_to_update=frozenset({"content_text"}),
        )
    )

    assert output.content_text == "Conteúdo atualizado."
    assert output.title == "Meu dia"
    assert output.updated_at == LATER
    uow.journal_entry_repository.update.assert_awaited_once_with(
        entry,
        frozenset({"content_text"}),
    )
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_update_entry_rejects_empty_update_before_opening_uow() -> None:
    uow = FakeJournalUnitOfWork()

    with pytest.raises(EmptyJournalUpdateError):
        await UpdateJournalEntryUseCase(uow, FixedClock()).execute(
            UpdateJournalEntryInputDTO(ENTRY_ID, USER_ID)
        )

    assert uow.enter_count == 0


@pytest.mark.asyncio
async def test_update_entry_rolls_back_when_entry_is_not_editable() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.find_by_id_for_user.return_value = make_entry(
        JournalEntryStatus.PENDING_ANALYSIS
    )

    with pytest.raises(JournalEntryNotEditableError):
        await UpdateJournalEntryUseCase(uow, FixedClock()).execute(
            UpdateJournalEntryInputDTO(
                ENTRY_ID,
                USER_ID,
                title="Novo título",
                fields_to_update=frozenset({"title"}),
            )
        )

    uow.journal_entry_repository.update.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_delete_entry_soft_deletes_and_commits() -> None:
    uow = FakeJournalUnitOfWork()
    entry = make_entry()
    uow.journal_entry_repository.find_by_id_for_user.return_value = entry

    await DeleteJournalEntryUseCase(uow, FixedClock()).execute(
        DeleteJournalEntryInputDTO(ENTRY_ID, USER_ID)
    )

    assert entry.status is JournalEntryStatus.DELETED
    assert entry.deleted_at == LATER
    uow.journal_entry_repository.soft_delete.assert_awaited_once_with(entry)
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_delete_entry_returns_not_found_without_committing() -> None:
    uow = FakeJournalUnitOfWork()
    uow.journal_entry_repository.find_by_id_for_user.return_value = None

    with pytest.raises(JournalEntryNotFoundError):
        await DeleteJournalEntryUseCase(uow, FixedClock()).execute(
            DeleteJournalEntryInputDTO(ENTRY_ID, USER_ID)
        )

    uow.journal_entry_repository.soft_delete.assert_not_awaited()
    uow.commit.assert_not_awaited()
