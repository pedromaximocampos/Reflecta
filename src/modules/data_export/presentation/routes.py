from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import SQLAlchemyError

from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.auth.public.data_export import AccountDataExportUnavailable
from src.modules.data_export.application import (
    ExportUserData,
    render_json_export,
    render_zip_export,
)
from src.modules.data_export.bootstrap import get_export_user_data


data_export_router = APIRouter(prefix="/account", tags=["Data portability"])
BRAZIL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


@data_export_router.get("/data-export")
async def export_user_data(
    format: Literal["zip", "json"] = Query(default="zip"),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case: ExportUserData = Depends(get_export_user_data),
):
    try:
        package = await use_case.execute(current_user.user_id.value)
    except AccountDataExportUnavailable:
        raise HTTPException(status_code=404, detail="Conta indisponível.") from None
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível exportar os dados agora. Tente novamente.",
        ) from None

    local_date = package.generated_at.astimezone(BRAZIL_TIMEZONE).date().isoformat()
    if format == "json":
        content = render_json_export(package)
        media_type = "application/json"
        extension = "json"
    else:
        content = render_zip_export(package)
        media_type = "application/zip"
        extension = "zip"

    filename = f"reflecta-meus-dados-{local_date}.{extension}"
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )
