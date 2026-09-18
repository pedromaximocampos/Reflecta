from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import Response

from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.journal.bootstrap.controllers import (
    get_create_journal_entry_controller,
    get_delete_journal_entry_controller,
    get_journal_entry_controller,
    get_list_journal_entries_controller,
    get_update_journal_entry_controller,
)
from src.modules.journal.presentation.controllers.create_journal_entry_controller import (
    CreateJournalEntryController,
)
from src.modules.journal.presentation.controllers.delete_journal_entry_controller import (
    DeleteJournalEntryController,
)
from src.modules.journal.presentation.controllers.get_journal_entry_controller import (
    GetJournalEntryController,
)
from src.modules.journal.presentation.controllers.list_journal_entries_controller import (
    ListJournalEntriesController,
)
from src.modules.journal.presentation.controllers.update_journal_entry_controller import (
    UpdateJournalEntryController,
)
from src.modules.journal.presentation.validators.journal_entry import (
    CreateJournalEntryValidator,
    JournalEntriesResponseValidator,
    JournalEntryResponseValidator,
    UpdateJournalEntryValidator,
)
from src.shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request

journal_router = APIRouter(prefix="/journal", tags=["Journal"])


@journal_router.post(
    "/entries",
    status_code=201,
    response_model=JournalEntryResponseValidator,
)
async def create_journal_entry(
    body: CreateJournalEntryValidator,
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: CreateJournalEntryController = Depends(
        get_create_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(mode="json"),
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.get(
    "/entries",
    response_model=JournalEntriesResponseValidator,
)
async def list_journal_entries(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: ListJournalEntriesController = Depends(
        get_list_journal_entries_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.get(
    "/entries/{journal_entry_id}",
    response_model=JournalEntryResponseValidator,
)
async def get_journal_entry(
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: GetJournalEntryController = Depends(get_journal_entry_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.patch(
    "/entries/{journal_entry_id}",
    response_model=JournalEntryResponseValidator,
)
async def update_journal_entry(
    body: UpdateJournalEntryValidator,
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: UpdateJournalEntryController = Depends(
        get_update_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(mode="json", exclude_unset=True),
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.delete(
    "/entries/{journal_entry_id}",
    status_code=204,
)
async def delete_journal_entry(
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: DeleteJournalEntryController = Depends(
        get_delete_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )
