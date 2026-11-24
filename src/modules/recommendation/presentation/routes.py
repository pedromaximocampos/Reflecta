from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j.exceptions import DriverError, Neo4jError
from sqlalchemy.exc import SQLAlchemyError

from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.modules.auth.public import AuthenticatedPrincipal
from src.modules.catalog.bootstrap.services import get_recommendation_work_catalog
from src.modules.catalog.bootstrap.unit_of_work import get_graph_unit_of_work
from src.modules.catalog.public.analysis_contextual_passage_catalog import (
    AnalysisContextualPassageCatalog,
)
from src.modules.journal.infrastructure.persistence.postgresql.dashboard_gateway import (
    JournalDashboardGateway,
)
from src.modules.recommendation.application import (
    ExploreWorks,
    GetRecommendationWork,
    RecommendWorks,
)
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


recommendation_router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


def get_recommend_works() -> RecommendWorks:
    work_catalog = get_recommendation_work_catalog()
    return RecommendWorks(
        journal=JournalDashboardGateway(individuum_mvp_provider),
        catalog=AnalysisContextualPassageCatalog(get_graph_unit_of_work()),
        works=work_catalog,
    )


def get_explore_works() -> ExploreWorks:
    return ExploreWorks(works=get_recommendation_work_catalog())


def get_recommendation_work() -> GetRecommendationWork:
    return GetRecommendationWork(works=get_recommendation_work_catalog())


@recommendation_router.get("/works")
async def recommend_works(
    limit: int = Query(default=4, ge=1, le=12),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case: RecommendWorks = Depends(get_recommend_works),
):
    try:
        return await use_case.execute(
            current_user.user_id.value,
            limit=limit,
            offset=offset,
        )
    except (SQLAlchemyError, Neo4jError, DriverError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Recomendações indisponíveis. Tente novamente mais tarde.",
        ) from None


@recommendation_router.get("/explore")
async def explore_works(
    limit: int = Query(default=6, ge=1, le=12),
    offset: int = Query(default=0, ge=0),
    _current_user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case: ExploreWorks = Depends(get_explore_works),
):
    try:
        return await use_case.execute(limit=limit, offset=offset)
    except (SQLAlchemyError, Neo4jError, DriverError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Catálogo indisponível. Tente novamente mais tarde.",
        ) from None


@recommendation_router.get("/works/{work_id}")
async def get_recommendation_work_details(
    work_id: str,
    _current_user: AuthenticatedPrincipal = Depends(get_current_user),
    use_case: GetRecommendationWork = Depends(get_recommendation_work),
):
    try:
        work = await use_case.execute(work_id)
    except (SQLAlchemyError, Neo4jError, DriverError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Catálogo indisponível. Tente novamente mais tarde.",
        ) from None
    if work is None:
        raise HTTPException(status_code=404, detail="Obra não encontrada.")
    return work

