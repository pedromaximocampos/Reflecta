from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from src.modules.ai_processing.application.processing_settings import AnalysisProcessingSettings
from src.modules.ai_processing.application.exceptions import (
    WorkIngestionProcessingStorageError,
)
from sqlalchemy.exc import SQLAlchemyError
from botocore.exceptions import BotoCoreError, ClientError
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


def get_failure_context_gateway():
    from src.modules.ai_processing.bootstrap.storage import get_work_ingestion_storage
    from src.modules.operations.infrastructure.work_ingestion_diagnostics_gateway import (
        WorkIngestionFailureContextGateway,
    )
    from src.shared.infrastructure.persistence.postgresql.provider import (
        individuum_mvp_provider,
    )
    return WorkIngestionFailureContextGateway(
        individuum_mvp_provider,
        get_work_ingestion_storage(),
    )


def get_operational_log_gateway():
    from src.modules.operations.infrastructure.work_ingestion_diagnostics_gateway import (
        CloudWatchOperationalLogGateway,
    )
    from src.shared.config.settings import get_settings
    settings = get_settings()
    return CloudWatchOperationalLogGateway(
        aws_region=settings.AWS_S3_REGION,
        log_group=settings.AWS_LOG_GROUP,
        aws_profile=settings.AWS_PROFILE,
    )


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


@operations_router.get("/context")
async def get_operational_failure_context(
    source: Source,
    failure_id: str = Query(..., min_length=1, max_length=300),
    admin: AuthenticatedPrincipal = Depends(require_admin),
    gateway=Depends(get_failure_context_gateway),
):
    try:
        result = await gateway.get_context(source, failure_id)
    except (
        SQLAlchemyError,
        BotoCoreError,
        ClientError,
        WorkIngestionProcessingStorageError,
    ):
        raise HTTPException(
            status_code=503,
            detail="Não foi possível recuperar o contexto da falha.",
        ) from None
    if result is None:
        raise HTTPException(status_code=404, detail="Falha não encontrada.")
    return result


@operations_router.get("/logs")
async def get_operational_failure_logs(
    source: Source,
    failure_id: str = Query(..., min_length=1, max_length=300),
    admin: AuthenticatedPrincipal = Depends(require_admin),
    failure_gateway=Depends(get_failure_gateway),
    log_gateway=Depends(get_operational_log_gateway),
):
    try:
        detail = await failure_gateway.detail(source, failure_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Falha não encontrada.")
        return await log_gateway.list_logs(detail)
    except HTTPException:
        raise
    except (SQLAlchemyError, BotoCoreError, ClientError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Não foi possível consultar os logs desta falha.",
        ) from None


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
