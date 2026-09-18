from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.use_cases.create_entry.dto import (
    CreateJournalEntryDTO,
)
from src.modules.journal.application.use_cases.create_entry.icreate_journal_entry_use_case import (
    ICreateJournalEntryUseCase,
)
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class CreateJournalEntryController(IControllerInterface):
    def __init__(self, use_case: ICreateJournalEntryUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        payload = dict(request.body or {})
        output = await self.__use_case.execute(
            CreateJournalEntryDTO(
                user_id=UserId(request.authenticated_user_id),
                title=payload.get("title"),
                content_text=payload["content_text"],
                context_tags=payload.get("context_tags"),
            )
        )
        return HttpResponse(status_code=201, body=output.to_dict())
