from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from src.modules.ai_processing.application.processing_settings import AnalysisProcessingSettings
from sqlalchemy.exc import SQLAlchemyError
from src.modules.auth.presentation.adapters.fast_api_auth import require_role
from src.modules.auth.public import AuthenticatedPrincipal, UserRole

Source = Literal["journal", "work_ingestion", "work_chunk", "inbox", "outbox"]
State = Literal["draft", "pending_analysis", "analysis_failed", "analyzed", "deleted",
                "pending", "processing", "failed", "completed", "pending_review", "processed",
                "PENDING", "PROCESSING", "SENT", "FAILED"]
require_admin = require_role(UserRole.ADMIN)
operations_router = APIRouter(prefix="/admin/operational-failures", tags=["Operational failures"])


def default_analysis_settings():
    from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAISettings
    settings = OpenAISettings()
    return AnalysisProcessingSettings(**{key: getattr(settings, key) for key in AnalysisProcessingSettings.model_fields})


@operations_router.get("/analysis-settings")
async def get_analysis_settings(admin: AuthenticatedPrincipal = Depends(require_admin)):
    return default_analysis_settings().model_dump()


def get_failure_gateway():
    from src.modules.operations.infrastructure.failure_gateway import OperationalFailureGateway
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
    return OperationalFailureGateway(individuum_mvp_provider)


@operations_router.get("")
async def list_operational_failures(
    source: Source | None = None, state: State | None = None,
    entity_id: str | None = Query(default=None, min_length=1, max_length=128),
    since: datetime | None = None, until: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0),
    admin: AuthenticatedPrincipal = Depends(require_admin), gateway=Depends(get_failure_gateway),
):
    if any(value is not None and value.tzinfo is None for value in (since, until)):
        raise HTTPException(status_code=422, detail="Informe datas com fuso horário.")
    if since is not None and until is not None and since > until:
        raise HTTPException(status_code=422, detail="A data inicial deve ser anterior à data final.")
    try:
        return await gateway.list_failures(source=source, state=state, entity_id=entity_id,
            since=since, until=until, limit=limit, offset=offset)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Consulta de falhas indisponível. Tente novamente.") from None


@operations_router.get("/{source}/{failure_id:path}")
async def get_operational_failure(
    source: Source, failure_id: str = Path(..., min_length=1, max_length=300),
    admin: AuthenticatedPrincipal = Depends(require_admin), gateway=Depends(get_failure_gateway),
):
    try:
        result = await gateway.detail(source, failure_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Consulta de falhas indisponível. Tente novamente.") from None
    if result is None:
        raise HTTPException(status_code=404, detail="Falha não encontrada.")
    return result


def get_reprocess_gateway():
    from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
    return JournalAnalysisGateway(individuum_mvp_provider)


@operations_router.post("/journal/{failure_id}/reprocess", status_code=202)
async def reprocess_journal_failure(
    failure_id: str = Path(..., min_length=26, max_length=26),
    body: AnalysisProcessingSettings | None = Body(default=None),
    admin: AuthenticatedPrincipal = Depends(require_admin), gateway=Depends(get_reprocess_gateway),
):
    from datetime import timezone
    from src.modules.journal.public.analysis import AnalysisConflictError
    from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
    try:
        settings = body if body is not None else default_analysis_settings()
        return await gateway.admin_reprocess(failure_id, admin.user_id.value, now=datetime.now(timezone.utc),
                                             processing_settings=settings.model_dump())
    except JournalEntryNotFoundError:
        raise HTTPException(status_code=404, detail="Falha não encontrada ou entrada indisponível.") from None
    except AnalysisConflictError:
        raise HTTPException(status_code=409, detail="Esta falha não é mais elegível. Atualize a lista.") from None
    except ValueError:
        raise HTTPException(status_code=400, detail="A reflexão não atende aos requisitos para análise.") from None
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Não foi possível solicitar o reprocessamento. Tente novamente.") from None
