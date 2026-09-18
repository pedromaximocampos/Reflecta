from src.modules.journal.bootstrap.use_cases import (
    get_create_journal_entry_use_case,
    get_delete_journal_entry_use_case,
    get_journal_entry_use_case,
    get_list_journal_entries_use_case,
    get_update_journal_entry_use_case,
)
from src.modules.journal.presentation.controllers.create_journal_entry_controller import (
    CreateJournalEntryController,
)
from src.modules.journal.presentation.controllers.delete_journal_entry_controller import (
    DeleteJournalEntryController,
)
from src.modules.journal.presentation.controllers.get_journal_entry_controller import (
    GetJournalEntryController,
)
from src.modules.journal.presentation.controllers.list_journal_entries_controller import (
    ListJournalEntriesController,
)
from src.modules.journal.presentation.controllers.update_journal_entry_controller import (
    UpdateJournalEntryController,
)


def get_create_journal_entry_controller() -> CreateJournalEntryController:
    return CreateJournalEntryController(get_create_journal_entry_use_case())


def get_journal_entry_controller() -> GetJournalEntryController:
    return GetJournalEntryController(get_journal_entry_use_case())


def get_list_journal_entries_controller() -> ListJournalEntriesController:
    return ListJournalEntriesController(get_list_journal_entries_use_case())


def get_update_journal_entry_controller() -> UpdateJournalEntryController:
    return UpdateJournalEntryController(get_update_journal_entry_use_case())


def get_delete_journal_entry_controller() -> DeleteJournalEntryController:
    return DeleteJournalEntryController(get_delete_journal_entry_use_case())
