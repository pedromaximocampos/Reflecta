from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.delete_entry.dto import (
    DeleteJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.delete_entry.idelete_journal_entry_use_case import (
    IDeleteJournalEntryUseCase,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class DeleteJournalEntryController(IControllerInterface):
    def __init__(self, use_case: IDeleteJournalEntryUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        await self.__use_case.execute(
            DeleteJournalEntryInputDTO(
                journal_entry_id=JournalEntryId(
                    str(request.path_params["journal_entry_id"])
                ),
                user_id=UserId(request.authenticated_user_id),
            )
        )
        return HttpResponse(status_code=204)
