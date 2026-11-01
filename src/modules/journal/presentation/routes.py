from src.modules.journal.public.context_analysis import ContextPeriod
from datetime import date
from datetime import datetime
import logging
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)
from src.modules.operations.presentation.routes import require_admin, get_failure_gateway
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request
from fastapi.responses import Response

from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.journal.bootstrap.controllers import (
    get_create_journal_entry_controller,
    get_delete_journal_entry_controller,
    get_journal_entry_controller,
    get_list_journal_entries_controller,
    get_update_journal_entry_controller,
)
from src.modules.journal.presentation.controllers.create_journal_entry_controller import (
    CreateJournalEntryController,
)
from src.modules.journal.presentation.controllers.delete_journal_entry_controller import (
    DeleteJournalEntryController,
)
from src.modules.journal.presentation.controllers.get_journal_entry_controller import (
    GetJournalEntryController,
)
from src.modules.journal.presentation.controllers.list_journal_entries_controller import (
    ListJournalEntriesController,
)
from src.modules.journal.presentation.controllers.update_journal_entry_controller import (
    UpdateJournalEntryController,
)
from src.modules.journal.presentation.validators.journal_entry import (
    CreateJournalEntryValidator,
    JournalEntriesResponseValidator,
    JournalEntryResponseValidator,
    UpdateJournalEntryValidator,
)
from src.shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request

journal_router = APIRouter(prefix="/journal", tags=["Journal"])


def get_analysis_gateway():
    from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
    return JournalAnalysisGateway(individuum_mvp_provider)


def get_context_gateway():
    from src.modules.journal.infrastructure.persistence.postgresql.context_gateway import ContextGateway
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
    return ContextGateway(individuum_mvp_provider)


def get_context_case():
    from src.modules.ai_processing.application.contextual_analysis import AnalyzeContext
    from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAIInterpreter, OpenAISettings
    return AnalyzeContext(get_context_gateway(), OpenAIInterpreter(OpenAISettings()))


def get_context_period(start_date: date, end_date: date):
    from pydantic import ValidationError
    try:
        return ContextPeriod(start_date=start_date, end_date=end_date)
    except ValidationError:
        raise HTTPException(status_code=422, detail="Selecione um período de exatamente 7 dias, incluindo início e fim.") from None


@journal_router.get("/context-analysis")
async def get_context_analysis(
    period: ContextPeriod = Depends(get_context_period),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_context_gateway),
):
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return await gateway.status(current_user.user_id.value, period)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Histórico indisponível. Tente novamente mais tarde.") from None


@journal_router.get("/context-analysis/history")
async def get_context_analysis_history(
    limit: int = Query(default=5, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_context_gateway),
):
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return await gateway.history(current_user.user_id.value, limit=limit, offset=offset)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Histórico de análises indisponível. Tente novamente mais tarde.") from None


@journal_router.post("/context-analysis")
async def submit_context_analysis(
    period: ContextPeriod,
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    case=Depends(get_context_case),
):
    from src.modules.ai_processing.application.contextual_analysis import InsufficientHistoryError, HistoryChangedError
    from src.modules.ai_processing.application.contracts import InterpretationFailedError, ProviderNotConfiguredError
    from sqlalchemy.exc import SQLAlchemyError
    from pydantic import ValidationError
    try:
        return await case.execute(current_user.user_id.value, period)
    except InsufficientHistoryError:
        raise HTTPException(status_code=409, detail="O período selecionado precisa conter pelo menos 5 reflexões para gerar a análise.") from None
    except HistoryChangedError:
        raise HTTPException(status_code=409, detail="Seu histórico mudou durante a análise. Solicite novamente.") from None
    except (InterpretationFailedError, ProviderNotConfiguredError, SQLAlchemyError, ValidationError) as error:
        if isinstance(error, InterpretationFailedError):
            code = error.reason.value
        elif isinstance(error, ProviderNotConfiguredError):
            code = "provider_not_configured"
        elif isinstance(error, SQLAlchemyError):
            code = "database_error"
        else:
            code = "invalid_interpretation"
        logger.warning("Context analysis failed code=%s", code)
        raise HTTPException(status_code=503, detail="Não foi possível analisar seu histórico. Suas reflexões foram preservadas. Tente novamente.") from None


@journal_router.get("/entries/{journal_entry_id}/analysis")
async def get_journal_analysis(
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_analysis_gateway),
):
    return await gateway.get_analysis(journal_entry_id, current_user.user_id.value)


@journal_router.get("/entries/{journal_entry_id}/analysis/failures", deprecated=True)
async def get_journal_analysis_failures(
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    limit: int = Query(default=20, ge=1, le=100),
    admin: AuthenticatedPrincipal = Depends(require_admin),
    gateway=Depends(get_failure_gateway),
):
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return await gateway.list_failures(source="journal", entity_id=journal_entry_id, limit=limit)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Consulta de falhas indisponível. Tente novamente.") from None


class AnalysisSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: datetime | None = None


@journal_router.post("/entries/{journal_entry_id}/analysis", status_code=202)
async def submit_journal_analysis(
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    body: AnalysisSubmission | None = Body(default=None),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    gateway=Depends(get_analysis_gateway),
):
    from datetime import timezone
    from src.modules.journal.public.analysis import AnalysisConflictError, UserReprocessLimitError
    from sqlalchemy.exc import SQLAlchemyError
    try:
        return await gateway.submit(journal_entry_id, current_user.user_id.value, now=datetime.now(timezone.utc),
                                    expected_revision=body.expected_revision if body else None)
    except UserReprocessLimitError:
        raise HTTPException(status_code=403, detail="Após três reprocessamentos sem sucesso, somente um administrador pode solicitar nova tentativa.") from None
    except AnalysisConflictError:
        raise HTTPException(status_code=409, detail="O estado da análise mudou. Atualize a página antes de tentar novamente.") from None
    except ValueError:
        raise HTTPException(status_code=400, detail="A reflexão deve conter entre 1 e 20000 caracteres.") from None
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Não foi possível solicitar a análise. Tente novamente.") from None


@journal_router.post(
    "/entries",
    status_code=201,
    response_model=JournalEntryResponseValidator,
)
async def create_journal_entry(
    body: CreateJournalEntryValidator,
    request: Request,
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: CreateJournalEntryController = Depends(
        get_create_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(mode="json"),
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.get(
    "/entries",
    response_model=JournalEntriesResponseValidator,
)
async def list_journal_entries(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: ListJournalEntriesController = Depends(
        get_list_journal_entries_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.get(
    "/entries/{journal_entry_id}",
    response_model=JournalEntryResponseValidator,
)
async def get_journal_entry(
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: GetJournalEntryController = Depends(get_journal_entry_controller),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.patch(
    "/entries/{journal_entry_id}",
    response_model=JournalEntryResponseValidator,
)
async def update_journal_entry(
    body: UpdateJournalEntryValidator,
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: UpdateJournalEntryController = Depends(
        get_update_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        body.model_dump(mode="json", exclude_unset=True),
        authenticated_user_id=current_user.user_id.value,
    )


@journal_router.delete(
    "/entries/{journal_entry_id}",
    status_code=204,
)
async def delete_journal_entry(
    request: Request,
    journal_entry_id: str = Path(..., min_length=26, max_length=26),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    controller: DeleteJournalEntryController = Depends(
        get_delete_journal_entry_controller
    ),
) -> Response:
    return await adapter_fastapi_request(
        request,
        controller.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )
