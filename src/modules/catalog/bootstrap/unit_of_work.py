from src.modules.catalog.infrastructure.persistence.neo4j.mappers.theme_mapper import ThemeMapper
from src.modules.catalog.infrastructure.persistence.neo4j.unit_of_work.neo4j_unit_of_work import (
    Neo4jUnitOfWork,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import ICatalogGraphUnitOfWork
from src.shared.infrastructure.persistence.neo4j.provider import reflecta_neo4j_provider



def get_graph_unit_of_work() -> ICatalogGraphUnitOfWork:
    return Neo4jUnitOfWork(
        reflecta_neo4j_provider,
        ThemeMapper(),
    )
