from src.modules.catalog.domain.ports.unit_of_work.icatalog_sql_unit_of_work import (
    ICatalogSQLUnitOfWork,
)
from src.modules.catalog.infrastructure.persistence.postgresql.mappers.work_ingestion_mapper import (
    WorkIngestionMapper,
)
from src.modules.catalog.infrastructure.persistence.postgresql.unit_of_work.catalog_sql_unit_of_work import (
    CatalogSQLUnitOfWork,
)
from src.modules.internal_events.infrastructure.persistence.postgresql.mappers.outbox_mapper import (
    OutboxMapper,
)
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.author_mapper import AuthorMapper
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.passage_mapper import PassageMapper
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.theme_mapper import ThemeMapper
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.work_mapper import WorkMapper
from src.modules.catalog.infrastructure.persistence.neo4j.unit_of_work.neo4j_unit_of_work import (
    Neo4jUnitOfWork,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import ICatalogGraphUnitOfWork
from src.shared.infrastructure.persistence.neo4j.provider import reflecta_neo4j_provider
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)
from src.shared.infrastructure.system.providers import get_clock



def get_graph_unit_of_work() -> ICatalogGraphUnitOfWork:
    return Neo4jUnitOfWork(
        reflecta_neo4j_provider,
        ThemeMapper(),
        WorkMapper(),
        AuthorMapper(),
        PassageMapper(),
    )


def get_sql_unit_of_work() -> ICatalogSQLUnitOfWork:
    return CatalogSQLUnitOfWork(
        db=individuum_mvp_provider,
        system_clock=get_clock(),
        work_ingestion_mapper=WorkIngestionMapper(),
        outbox_mapper=OutboxMapper(),
    )
