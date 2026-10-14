from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import Response

from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.catalog.bootstrap.controllers import (
    get_all_themes_controller,
    get_create_themes_controller,
    get_create_work_controller,
    get_request_work_ingestion_controller,
    get_delete_theme_by_id_controller,
    get_theme_by_id_controller,
    get_update_theme_controller,
    get_activate_passage_controller,
    get_approve_passage_controller,
    get_create_passage_controller,
    get_deactivate_passage_controller,
    get_delete_passage_controller,
    get_list_passages_controller,
    get_passage_controller,
    get_reject_passage_controller,
    get_update_passage_controller,
)
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.presentation.controllers.passage_controller import (
    CreatePassageController,
    DeletePassageController,
    GetPassageController,
    ListPassagesController,
    ReviewPassageController,
    SetPassageAvailabilityController,
    UpdatePassageController,
)
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)
from src.modules.catalog.presentation.controllers.create_work_controller import CreateWorkController
from src.modules.catalog.presentation.controllers.request_work_ingestion_controller import (
    RequestWorkIngestionController,
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
from src.modules.catalog.presentation.validators.create_work import CreatedWorkValidator, CreateWorkValidator
from src.modules.catalog.presentation.validators.request_work_ingestion import (
    ValidatedWorkDocumentUpload,
    WorkIngestionAcceptedValidator,
    validate_work_document_upload,
)
from src.modules.catalog.presentation.validators.passage import (
    CreatePassageValidator,
    PassageResponseValidator,
    PassagesResponseValidator,
    UpdatePassageValidator,
)
from src.shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request

catalog_router = APIRouter(prefix="/catalog", tags=["Catalog"])


@catalog_router.post(
    "/passages",
    summary="Create a manually curated passage",
    response_model=PassageResponseValidator,
    status_code=201,
)
async def create_passage(
    body: CreatePassageValidator,
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: CreatePassageController = Depends(get_create_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(),
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.get(
    "/passages",
    summary="List catalog passages",
    response_model=PassagesResponseValidator,
)
async def list_passages(
    request: Request,
    status: CatalogStatus | None = Query(default=None),
    work_id: str | None = Query(default=None, min_length=26, max_length=26),
    ingestion_id: str | None = Query(default=None, min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: ListPassagesController = Depends(get_list_passages_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.get(
    "/passages/{passage_id}",
    summary="Get a catalog passage",
    response_model=PassageResponseValidator,
)
async def get_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: GetPassageController = Depends(get_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.patch(
    "/passages/{passage_id}",
    summary="Adjust passage content or theme associations",
    response_model=PassageResponseValidator,
)
async def update_passage(
    body: UpdatePassageValidator,
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: UpdatePassageController = Depends(get_update_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(exclude_unset=True),
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/passages/{passage_id}/approve",
    summary="Approve an AI passage suggestion",
    response_model=PassageResponseValidator,
)
async def approve_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: ReviewPassageController = Depends(get_approve_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/passages/{passage_id}/reject",
    summary="Reject an AI passage suggestion",
    response_model=PassageResponseValidator,
)
async def reject_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: ReviewPassageController = Depends(get_reject_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/passages/{passage_id}/activate",
    summary="Make an approved passage available",
    response_model=PassageResponseValidator,
)
async def activate_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: SetPassageAvailabilityController = Depends(
        get_activate_passage_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/passages/{passage_id}/deactivate",
    summary="Remove a passage from active catalog use",
    response_model=PassageResponseValidator,
)
async def deactivate_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: SetPassageAvailabilityController = Depends(
        get_deactivate_passage_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.delete(
    "/passages/{passage_id}",
    summary="Logically remove a catalog passage",
    status_code=204,
)
async def delete_passage(
    request: Request,
    passage_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: DeletePassageController = Depends(get_delete_passage_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/works",
    summary="Create catalog work metadata",
    response_model=CreatedWorkValidator,
    status_code=201,
)
async def create_work(
    body: CreateWorkValidator,
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: CreateWorkController = Depends(get_create_work_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(),
        authenticated_user_id=current_user.user_id.value,
    )


@catalog_router.post(
    "/works/{work_id}/ingestions",
    summary="Request processing of a catalog work document",
    response_model=WorkIngestionAcceptedValidator,
    status_code=202,
)
async def request_work_ingestion(
    request: Request,
    work_id: str = Path(..., min_length=26, max_length=26),
    document: ValidatedWorkDocumentUpload = Depends(
        validate_work_document_upload
    ),
    current_user: AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN)),
    controller: RequestWorkIngestionController = Depends(
        get_request_work_ingestion_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        {
            "filename": document.filename,
            "content_type": document.content_type,
            "size_bytes": document.size_bytes,
            "content": document.content,
        },
        authenticated_user_id=current_user.user_id.value,
    )


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
