from src.modules.journal.infrastructure.persistence.postgresql.dashboard_gateway import (
    JournalDashboardGateway,
)
from src.modules.journal.public.dashboard import IJournalHomeReader
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


def get_journal_home_reader() -> IJournalHomeReader:
    return JournalDashboardGateway(individuum_mvp_provider)
