from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.catalog.bootstrap.controllers import get_create_themes_controller
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)
from src.modules.catalog.presentation.validators.create_theme import (
    CreateThemesResponseValidator,
    CreateThemesValidator,
)
from src.shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request

catalog_router = APIRouter(prefix="/catalog", tags=["Catalog"])


@catalog_router.post(
    "/themes",
    summary="Create canonical themes",
    response_model=CreateThemesResponseValidator,
    status_code=201,
)
async def create_themes(
    body: CreateThemesValidator,
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: CreateThemesController = Depends(get_create_themes_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(),
        authenticated_user_id=current_user.user_id.value,
    )
