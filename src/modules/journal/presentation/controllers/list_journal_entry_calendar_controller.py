from datetime import date

from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.list_entry_calendar.dto import (
    ListJournalEntryCalendarInputDTO,
)
from src.modules.journal.application.use_cases.list_entry_calendar.list_journal_entry_calendar_use_case import (
    ListJournalEntryCalendarUseCase,
)
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ListJournalEntryCalendarController(IControllerInterface):
    def __init__(self, use_case: ListJournalEntryCalendarUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        output = await self.__use_case.execute(
            ListJournalEntryCalendarInputDTO(
                user_id=UserId(request.authenticated_user_id),
                start_date=date.fromisoformat(request.query_params["start_date"]),
                end_date=date.fromisoformat(request.query_params["end_date"]),
            )
        )
        return HttpResponse(status_code=200, body=output.to_dict())
