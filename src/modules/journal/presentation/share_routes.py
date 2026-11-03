from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.journal.infrastructure.persistence.postgresql.share_gateway import ContextShareGateway, ShareUnavailable, ShareIneligible

share_router = APIRouter(tags=["Context sharing"])


def get_share_gateway():
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
    return ContextShareGateway(individuum_mvp_provider)


class Confirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmed: Literal[True]


class ShareToken(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=43, max_length=43, pattern=r"^[A-Za-z0-9_-]+$")


def private_response(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"


HEADERS = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex, nofollow"}


def translate(error):
    if isinstance(error, ShareUnavailable):
        return HTTPException(status_code=404, headers=HEADERS, detail="Compartilhamento indisponível ou link inválido, expirado ou revogado.")
    if isinstance(error, ShareIneligible):
        return HTTPException(status_code=409, headers=HEADERS, detail="Esta análise não está disponível para compartilhamento.")
    return HTTPException(status_code=503, headers=HEADERS, detail="Não foi possível acessar o compartilhamento. Tente novamente.")


@share_router.post("/journal/context-analyses/{analysis_id}/shares", status_code=201)
async def create_share(body: Confirmation, response: Response,
    analysis_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user), gateway=Depends(get_share_gateway)):
    private_response(response)
    try:
        return await gateway.create(analysis_id, user.user_id.value)
    except (ShareUnavailable, ShareIneligible, SQLAlchemyError, ValidationError) as error:
        raise translate(error) from None


@share_router.get("/journal/context-analyses/{analysis_id}/shares")
async def list_shares(response: Response, analysis_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user), gateway=Depends(get_share_gateway)):
    private_response(response)
    try:
        return await gateway.list_shares(analysis_id, user.user_id.value)
    except (ShareUnavailable, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.delete("/journal/context-analyses/{analysis_id}/shares/{share_id}")
async def revoke_share(response: Response, analysis_id: str = Path(..., min_length=26, max_length=26),
    share_id: str = Path(..., min_length=26, max_length=26),
    user: AuthenticatedPrincipal = Depends(get_current_user), gateway=Depends(get_share_gateway)):
    private_response(response)
    try:
        return await gateway.revoke(analysis_id, share_id, user.user_id.value)
    except (ShareUnavailable, SQLAlchemyError) as error:
        raise translate(error) from None


@share_router.post("/shared/context-analysis/resolve")
async def resolve_share(body: ShareToken, response: Response, gateway=Depends(get_share_gateway)):
    private_response(response)
    try:
        return await gateway.resolve(body.token)
    except (ShareUnavailable, SQLAlchemyError, ValidationError, KeyError, TypeError) as error:
        raise translate(error) from None
