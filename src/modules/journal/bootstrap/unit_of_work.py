from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.modules.journal.infrastructure.persistence.postgresql.mappers.journal_entry_mapper import (
    JournalEntryMapper,
)
from src.modules.journal.infrastructure.persistence.postgresql.units_of_work.journal_unit_of_work import (
    JournalUnitOfWork,
)
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


def get_journal_unit_of_work() -> IJournalUnitOfWork:
    return JournalUnitOfWork(
        db=individuum_mvp_provider,
        journal_entry_mapper=JournalEntryMapper(),
    )
