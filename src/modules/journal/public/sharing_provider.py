from functools import lru_cache

from src.modules.journal.infrastructure.persistence.postgresql.journal_sharing_facade import (
    PostgresJournalSharingFacade,
)
from src.modules.journal.public.context_share import IJournalSharingFacade
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


@lru_cache
def get_journal_sharing_facade() -> IJournalSharingFacade:
    """Expose Journal's sharing capability without leaking its persistence model."""
    return PostgresJournalSharingFacade(individuum_mvp_provider)

