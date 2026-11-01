from src.modules.ai_processing.application.contracts import ITextInterpreter
from src.modules.ai_processing.application.contextual_passage_selection import (
    IContextualPassageSelector,
)
from src.modules.ai_processing.application.interpret_entry import InterpretEntry
from src.modules.ai_processing.application.use_cases.process_work_ingestion import (
    ProcessWorkIngestionUseCase,
)
from src.modules.ai_processing.application.use_cases.list_work_ingestions import (
    ListWorkIngestionsUseCase,
)
from src.modules.ai_processing.bootstrap.analysis import get_work_passage_analyzer
from src.modules.ai_processing.bootstrap.catalog import (
    get_analysis_theme_catalog,
    get_contextual_passage_catalog,
    get_passage_candidate_catalog,
    get_work_ingestion_catalog,
    get_work_ingestion_query_catalog,
)
from src.modules.ai_processing.bootstrap.document import (
    get_document_text_extractor,
    get_text_chunker,
    get_text_normalizer,
)
from src.modules.ai_processing.bootstrap.storage import get_work_ingestion_storage
from src.modules.ai_processing.bootstrap.unit_of_work import (
    get_ai_processing_unit_of_work,
)
from src.modules.ai_processing.infrastructure.openai_interpreter import (
    OpenAIInterpreter,
    OpenAISettings,
)
from src.shared.config.settings import get_settings
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator


def get_interpret_entry(
    interpreter: ITextInterpreter | None = None,
    passage_selector: IContextualPassageSelector | None = None,
    *, processing_settings: dict | None = None,
) -> InterpretEntry:
    # Lazy imports keep the application contracts independent from environment setup.
    from src.modules.catalog.bootstrap.unit_of_work import get_graph_unit_of_work
    from src.modules.catalog.public.analysis_catalog import AnalysisThemeCatalog
    from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import (
        JournalAnalysisGateway,
    )
    from src.shared.infrastructure.persistence.postgresql.provider import (
        individuum_mvp_provider,
    )
    from src.shared.infrastructure.system.system_clock import SystemClock
    from src.shared.infrastructure.system.ulid_generator import UlidGenerator

    settings = (
        OpenAISettings()
        if interpreter is None or passage_selector is None
        else None
    )
    if processing_settings is not None and settings is not None:
        from src.modules.ai_processing.application.processing_settings import AnalysisProcessingSettings
        overrides = AnalysisProcessingSettings.model_validate(processing_settings).model_dump()
        settings = settings.model_copy(update=overrides)
    provider = OpenAIInterpreter(settings) if settings is not None else None
    return InterpretEntry(
        journal=JournalAnalysisGateway(individuum_mvp_provider),
        catalog=AnalysisThemeCatalog(get_graph_unit_of_work()),
        passage_catalog=get_contextual_passage_catalog(),
        interpreter=interpreter if interpreter is not None else provider,
        passage_selector=(
            passage_selector if passage_selector is not None else provider
        ),
        clock=SystemClock(),
        ids=UlidGenerator(),
        timeout_seconds=(
            settings.timeout_seconds if settings is not None else 30
        ),
    )


def get_process_work_ingestion_use_case() -> ProcessWorkIngestionUseCase:
    settings = get_settings()
    return ProcessWorkIngestionUseCase(
        ai_processing_uow=get_ai_processing_unit_of_work(),
        work_ingestion_storage=get_work_ingestion_storage(),
        document_text_extractor=get_document_text_extractor(),
        text_normalizer=get_text_normalizer(),
        text_chunker=get_text_chunker(),
        theme_catalog=get_analysis_theme_catalog(),
        passage_analyzer=get_work_passage_analyzer(),
        passage_candidate_catalog=get_passage_candidate_catalog(),
        work_ingestion_catalog=get_work_ingestion_catalog(),
        ulid_generator=get_ulid_generator(),
        clock=get_clock(),
        chunk_lease_seconds=settings.AI_WORK_INGESTION_CHUNK_LEASE_SECONDS,
    )


def get_list_work_ingestions_use_case() -> ListWorkIngestionsUseCase:
    from src.modules.operations.infrastructure.failure_gateway import (
        OperationalFailureGateway,
    )
    from src.shared.infrastructure.persistence.postgresql.provider import (
        individuum_mvp_provider,
    )

    return ListWorkIngestionsUseCase(
        catalog=get_work_ingestion_query_catalog(),
        ai_processing_uow=get_ai_processing_unit_of_work(),
        failure_query=OperationalFailureGateway(individuum_mvp_provider),
    )
