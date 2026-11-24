from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.sharing.application import (
    AssignProfessionalActivitiesCommand,
    ListProfessionalActivitiesQuery,
    ProfessionalActivityInput,
)
from src.modules.sharing.bootstrap import (
    get_assign_professional_activities,
    get_complete_professional_activity,
    get_list_professional_activities,
    get_share_gateway,
)
from src.modules.sharing.domain import (
    ActivityLimitReached,
    ProfessionalActivityNotFound,
    ShareIneligible,
    ShareUnavailable,
)
from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus


share_router = APIRouter(tags=["Context sharing"])


class Confirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmed: Literal[True]
    include_journals: bool = False


class ShareToken(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=43, max_length=43, pattern=r"^[A-Za-z0-9_-]+$")


CleanTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=160),
]
CleanDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=10, max_length=4000),
]


class ProfessionalActivityItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: ActivityKind
    title: CleanTitle
    description: CleanDescription
    due_date: date | None = None


class ProfessionalActivitiesRequest(ShareToken):
    activities: list[ProfessionalActivityItemRequest] = Field(
        min_length=1,
        max_length=20,
    )


def private_response(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"


HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Robots-Tag": "noindex, nofollow",
}


def translate(error: Exception) -> HTTPException:
    if isinstance(error, ShareUnavailable):
        return HTTPException(
            status_code=404,
            headers=HEADERS,
            detail="Compartilhamento indisponível ou link inválido, expirado ou revogado.",
        )
    if isinstance(error, ShareIneligible):
        return HTTPException(
            status_code=409,
            headers=HEADERS,
            detail="Esta análise não está disponível para compartilhamento.",
        )
    if isinstance(error, ActivityLimitReached):
        return HTTPException(
            status_code=409,
            headers=HEADERS,
            detail="Este acesso atingiu o limite de atividades e reflexões guiadas.",
        )
    if isinstance(error, ProfessionalActivityNotFound):
        return HTTPException(
            status_code=404,
            headers=HEADERS,
            detail="Orientação não encontrada.",
        )
    return HTTPException(
        status_code=503,
        headers=HEADERS,
        detail="Não foi possível acessar o compartilhamento. Tente novamente.",
    )


def serialize_activity(activity: ProfessionalActivity) -> dict:
    return {
        "id": activity.id,
        "kind": activity.kind.value,
        "title": activity.title,
        "description": activity.description,
        "due_date": activity.due_date.isoformat() if activity.due_date else None,
        "status": activity.status.value,
        "created_at": activity.created_at.isoformat(),
        "completed_at": (
            activity.completed_at.isoformat()
            if activity.completed_at
            else None
        ),
    }


@share_router.post("/journal/context-analyses/{analysis_id}/shares", status_code=201)
async def create_share(
    body: Confirmation,
    response: Response,
    analysis_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_share_gateway),
):
    private_response(response)
    try:
        return await gateway.create(
            analysis_id,
            user.user_id.value,
            include_journals=body.include_journals,
        )
    except (ShareUnavailable, ShareIneligible, SQLAlchemyError, ValidationError) as error:
        raise translate(error) from None


@share_router.get("/journal/context-shares")
async def list_owner_shares(
    response: Response,
    state: Literal["active", "expired", "revoked"] | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_share_gateway),
):
    private_response(response)
    try:
        return await gateway.list_owner_shares(
            user.user_id.value,
            state=state,
            limit=limit,
            offset=offset,
        )
    except (SQLAlchemyError, ValueError) as error:
        raise translate(error) from None


@share_router.get("/journal/context-analyses/{analysis_id}/shares")
async def list_shares(
    response: Response,
    analysis_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_share_gateway),
):
    private_response(response)
    try:
        return await gateway.list_shares(analysis_id, user.user_id.value)
    except (ShareUnavailable, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.delete("/journal/context-analyses/{analysis_id}/shares/{share_id}")
async def revoke_share(
    response: Response,
    analysis_id: str = Path(..., min_length=26, max_length=26),
    share_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_share_gateway),
):
    private_response(response)
    try:
        return await gateway.revoke(analysis_id, share_id, user.user_id.value)
    except (ShareUnavailable, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.post("/journal/context-analyses/{analysis_id}/shares/{share_id}/rotate")
async def rotate_share_token(
    response: Response,
    analysis_id: str = Path(..., min_length=26, max_length=26),
    share_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_share_gateway),
):
    """Replace a legacy token and return a link token recoverable by its owner."""
    private_response(response)
    try:
        return await gateway.rotate_token(
            analysis_id,
            share_id,
            user.user_id.value,
        )
    except (ShareUnavailable, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.post("/shared/context-analysis/resolve")
async def resolve_share(
    body: ShareToken,
    response: Response,
    gateway=Depends(get_share_gateway),
):
    private_response(response)
    try:
        return await gateway.resolve(body.token)
    except (
        ShareUnavailable,
        SQLAlchemyError,
        ValidationError,
        KeyError,
        TypeError,
    ) as error:
        raise translate(error) from None


@share_router.post("/shared/professional-activities", status_code=201)
async def create_professional_activities(
    body: ProfessionalActivitiesRequest,
    response: Response,
    use_case=Depends(get_assign_professional_activities),
):
    private_response(response)
    try:
        activities = await use_case.execute(
            AssignProfessionalActivitiesCommand(
                token=body.token,
                activities=tuple(
                    ProfessionalActivityInput(
                        kind=item.kind,
                        title=item.title,
                        description=item.description,
                        due_date=item.due_date,
                    )
                    for item in body.activities
                ),
            )
        )
        return {
            "count": len(activities),
            "activities": [serialize_activity(activity) for activity in activities],
        }
    except (ShareUnavailable, ActivityLimitReached, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.get("/sharing/professional-activities")
async def list_professional_activities(
    response: Response,
    status: ActivityStatus | None = Query(default=None),
    limit: int = Query(default=8, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case=Depends(get_list_professional_activities),
):
    private_response(response)
    try:
        page = await use_case.execute(
            ListProfessionalActivitiesQuery(
                user_id=user.user_id.value,
                status=status,
                limit=limit,
                offset=offset,
            )
        )
        return {
            "activities": [
                serialize_activity(activity)
                for activity in page.activities
            ],
            "total": page.total,
            "limit": page.limit,
            "offset": page.offset,
        }
    except SQLAlchemyError as error:
        raise translate(error) from None


@share_router.patch("/sharing/professional-activities/{activity_id}/complete")
async def complete_professional_activity(
    response: Response,
    activity_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case=Depends(get_complete_professional_activity),
):
    private_response(response)
    try:
        activity = await use_case.execute(activity_id, user.user_id.value)
        return serialize_activity(activity)
    except (ProfessionalActivityNotFound, SQLAlchemyError) as error:
        raise translate(error) from None
