from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.list_entries.dto import (
    ListJournalEntriesInputDTO,
)
from src.modules.journal.application.use_cases.list_entries.ilist_journal_entries_use_case import (
    IListJournalEntriesUseCase,
)
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ListJournalEntriesController(IControllerInterface):
    def __init__(self, use_case: IListJournalEntriesUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        output = await self.__use_case.execute(
            ListJournalEntriesInputDTO(
                user_id=UserId(request.authenticated_user_id),
                limit=int(request.query_params.get("limit", 50)),
                offset=int(request.query_params.get("offset", 0)),
            )
        )
        return HttpResponse(status_code=200, body=output.to_dict())
