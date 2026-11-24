from functools import lru_cache

from src.modules.auth.bootstrap.storage import get_user_avatar_storage
from src.modules.auth.infrastructure.persistence.postgresql.account_data_export_facade import (
    PostgresAccountDataExportFacade,
)
from src.modules.data_export.application import ExportUserData
from src.modules.journal.infrastructure.persistence.postgresql.journal_data_export_facade import (
    PostgresJournalDataExportFacade,
)
from src.modules.sharing.infrastructure.persistence.postgresql.sharing_data_export_facade import (
    PostgresSharingDataExportFacade,
)
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)
from src.shared.infrastructure.system.providers import get_clock


@lru_cache
def get_export_user_data() -> ExportUserData:
    return ExportUserData(
        account=PostgresAccountDataExportFacade(
            individuum_mvp_provider,
            get_user_avatar_storage(),
        ),
        journal=PostgresJournalDataExportFacade(individuum_mvp_provider),
        sharing=PostgresSharingDataExportFacade(individuum_mvp_provider),
        clock=get_clock(),
    )
