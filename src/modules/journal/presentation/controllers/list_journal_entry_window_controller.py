from datetime import date

from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.list_entry_window.dto import (
    ListJournalEntryWindowInputDTO,
)
from src.modules.journal.application.use_cases.list_entry_window.list_journal_entry_window_use_case import (
    ListJournalEntryWindowUseCase,
)
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ListJournalEntryWindowController(IControllerInterface):
    def __init__(self, use_case: ListJournalEntryWindowUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        raw_end_date = request.query_params.get("end_date")
        raw_center_date = request.query_params.get("center_date")
        output = await self.__use_case.execute(
            ListJournalEntryWindowInputDTO(
                user_id=UserId(request.authenticated_user_id),
                end_date=date.fromisoformat(raw_end_date) if raw_end_date else None,
                days=int(request.query_params.get("days", 15)),
                center_date=(
                    date.fromisoformat(raw_center_date)
                    if raw_center_date
                    else None
                ),
                before_days=int(request.query_params.get("before_days", 15)),
                after_days=int(request.query_params.get("after_days", 15)),
            )
        )
        return HttpResponse(status_code=200, body=output.to_dict())
