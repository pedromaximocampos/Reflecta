from src.modules.auth.public.data_export import IAccountDataExportFacade
from src.modules.journal.public.data_export import IJournalDataExportFacade
from src.modules.sharing.public.data_export import ISharingDataExportFacade
from src.shared.domain.ports.system.iclock import IClock

from .models import UserDataExportPackage


class ExportUserData:
    def __init__(
        self,
        *,
        account: IAccountDataExportFacade,
        journal: IJournalDataExportFacade,
        sharing: ISharingDataExportFacade,
        clock: IClock,
    ) -> None:
        self._account = account
        self._journal = journal
        self._sharing = sharing
        self._clock = clock

    async def execute(self, user_id: str) -> UserDataExportPackage:
        generated_at = self._clock.now()
        account = await self._account.export_account(user_id)
        journal = await self._journal.export_journal(user_id)
        sharing = await self._sharing.export_sharing(
            user_id,
            generated_at=generated_at,
        )
        return UserDataExportPackage(
            generated_at=generated_at,
            account=account,
            journal=journal,
            sharing=sharing,
        )
