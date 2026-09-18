from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.update_entry.dto import (
    UpdateJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.update_entry.iupdate_journal_entry_use_case import (
    IUpdateJournalEntryUseCase,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class UpdateJournalEntryController(IControllerInterface):
    def __init__(self, use_case: IUpdateJournalEntryUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        payload = dict(request.body or {})
        output = await self.__use_case.execute(
            UpdateJournalEntryInputDTO(
                journal_entry_id=JournalEntryId(
                    str(request.path_params["journal_entry_id"])
                ),
                user_id=UserId(request.authenticated_user_id),
                title=payload.get("title"),
                content_text=payload.get("content_text"),
                context_tags=payload.get("context_tags"),
                fields_to_update=frozenset(payload),
            )
        )
        return HttpResponse(status_code=200, body=output.to_dict())
