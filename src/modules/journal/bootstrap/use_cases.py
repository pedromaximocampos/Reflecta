from src.modules.journal.application.use_cases.create_entry.create_journal_entry_use_case_impl import (
    CreateJournalEntryUseCaseImpl,
)
from src.modules.journal.application.use_cases.delete_entry.delete_journal_entry_use_case import (
    DeleteJournalEntryUseCase,
)
from src.modules.journal.application.use_cases.get_entry.get_journal_entry_use_case import (
    GetJournalEntryUseCase,
)
from src.modules.journal.application.use_cases.list_entries.list_journal_entries_use_case import (
    ListJournalEntriesUseCase,
)
from src.modules.journal.application.use_cases.update_entry.update_journal_entry_use_case import (
    UpdateJournalEntryUseCase,
)
from src.modules.journal.bootstrap.unit_of_work import get_journal_unit_of_work
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator


def get_create_journal_entry_use_case() -> CreateJournalEntryUseCaseImpl:
    return CreateJournalEntryUseCaseImpl(
        journal_unit_of_work=get_journal_unit_of_work(),
        system_clock=get_clock(),
        ulid_generator=get_ulid_generator(),
    )


def get_journal_entry_use_case() -> GetJournalEntryUseCase:
    return GetJournalEntryUseCase(journal_unit_of_work=get_journal_unit_of_work())


def get_list_journal_entries_use_case() -> ListJournalEntriesUseCase:
    return ListJournalEntriesUseCase(
        journal_unit_of_work=get_journal_unit_of_work()
    )


def get_update_journal_entry_use_case() -> UpdateJournalEntryUseCase:
    return UpdateJournalEntryUseCase(
        journal_unit_of_work=get_journal_unit_of_work(),
        system_clock=get_clock(),
    )


def get_delete_journal_entry_use_case() -> DeleteJournalEntryUseCase:
    return DeleteJournalEntryUseCase(
        journal_unit_of_work=get_journal_unit_of_work(),
        system_clock=get_clock(),
    )
