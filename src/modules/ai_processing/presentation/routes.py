from fastapi import APIRouter, Depends, Query, Request, Response

from src.modules.ai_processing.bootstrap.controllers import (
    get_list_work_ingestions_controller,
)
from src.modules.ai_processing.presentation.controllers import (
    ListWorkIngestionsController,
)
from src.modules.ai_processing.presentation.validators import (
    WorkIngestionsResponseValidator,
)
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.shared.presentation.fast_api.fast_api_adapter import (
    adapter_fastapi_request,
)


ai_processing_router = APIRouter(
    prefix="/ai-processing",
    tags=["AI Processing"],
)


@ai_processing_router.get(
    "/work-ingestions",
    summary="List recent work ingestions with chunk progress",
    response_model=WorkIngestionsResponseValidator,
)
async def list_work_ingestions(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: ListWorkIngestionsController = Depends(
        get_list_work_ingestions_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )
