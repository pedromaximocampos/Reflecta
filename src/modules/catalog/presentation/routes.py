from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import Response

from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.catalog.bootstrap.controllers import (
    get_all_themes_controller,
    get_create_themes_controller,
    get_delete_theme_by_id_controller,
    get_theme_by_id_controller,
    get_update_theme_controller,
)
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)
from src.modules.catalog.presentation.controllers.delete_themes_controller import (
    DeleteThemeByIdController,
)
from src.modules.catalog.presentation.controllers.get_themes_controller import (
    GetAllThemesController,
    GetThemeByIdController,
)
from src.modules.catalog.presentation.controllers.update_theme_controller import (
    UpdateThemeController,
)
from src.modules.catalog.presentation.validators.create_theme import (
    CreateThemesResponseValidator,
    CreateThemesValidator,
    CreatedThemeValidator,
    ThemesResponseValidator,
)
from src.modules.catalog.presentation.validators.update_theme import UpdateThemeValidator
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


@catalog_router.get(
    "/themes",
    summary="List canonical themes",
    response_model=ThemesResponseValidator,
)
async def get_all_themes(
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: GetAllThemesController = Depends(get_all_themes_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.get(
    "/themes/{theme_id}",
    summary="Get a canonical theme by ID",
    response_model=CreatedThemeValidator,
)
async def get_theme_by_id(
    request: Request,
    theme_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: GetThemeByIdController = Depends(get_theme_by_id_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.patch(
    "/themes/{theme_id}",
    summary="Update a canonical theme",
    response_model=CreatedThemeValidator,
)
async def update_theme(
    body: UpdateThemeValidator,
    request: Request,
    theme_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: UpdateThemeController = Depends(get_update_theme_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(exclude_unset=True),
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.delete(
    "/themes/{theme_id}",
    summary="Delete a canonical theme",
    status_code=204,
)
async def delete_theme_by_id(
    request: Request,
    theme_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: DeleteThemeByIdController = Depends(
        get_delete_theme_by_id_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )
