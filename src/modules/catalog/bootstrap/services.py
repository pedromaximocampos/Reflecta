from src.modules.catalog.bootstrap.storage import get_work_cover_storage
from src.modules.catalog.bootstrap.unit_of_work import get_graph_unit_of_work
from src.modules.catalog.public import IRecommendationWorkCatalog
from src.modules.catalog.public.analysis_recommendation_work_catalog import (
    AnalysisRecommendationWorkCatalog,
)


def get_recommendation_work_catalog() -> IRecommendationWorkCatalog:
    return AnalysisRecommendationWorkCatalog(
        uow=get_graph_unit_of_work(),
        cover_storage=get_work_cover_storage(),
    )
