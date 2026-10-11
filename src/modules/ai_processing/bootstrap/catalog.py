from src.modules.ai_processing.application.ports.catalog import (
    IPassageCandidateCatalog,
    IWorkIngestionCatalog,
)
from src.modules.catalog.bootstrap.unit_of_work import (
    get_graph_unit_of_work,
    get_sql_unit_of_work,
)
from src.modules.catalog.public.analysis_catalog import AnalysisThemeCatalog
from src.modules.catalog.public.analysis_passage_catalog import AnalysisPassageCatalog
from src.modules.catalog.public.analysis_work_ingestion_catalog import (
    AnalysisWorkIngestionCatalog,
)
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator


def get_analysis_theme_catalog() -> AnalysisThemeCatalog:
    return AnalysisThemeCatalog(get_graph_unit_of_work())


def get_passage_candidate_catalog() -> IPassageCandidateCatalog:
    return AnalysisPassageCatalog(
        uow=get_graph_unit_of_work(),
        ids=get_ulid_generator(),
        clock=get_clock(),
    )


def get_work_ingestion_catalog() -> IWorkIngestionCatalog:
    return AnalysisWorkIngestionCatalog(get_sql_unit_of_work())
