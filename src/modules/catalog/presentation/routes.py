from _colorize import Theme

from fastapi import APIRouter, Depends, Request, Query

from shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.catalog.presentation.validators.create_theme import CreateThemesResponseValidator, CreateThemesValidator

catalog_router = APIRouter(prefix="/catalog", tags=["Catalog"])



@catalog_router.post("/themes", summary="Create a new themes", response_model=CreateThemesResponseValidator)
async def create_themes(
        body: CreateThemesValidator,
        request: Request,
        current_user:  AuthenticatedPrincipal = Depends(require_role(UserRole.ADMIN))
):
    return await adapter_fastapi_request(request,..., body,
                                         authenticated_user_id=current_user.user_id.value)