from collections.abc import Mapping
from typing import Any

from neo4j import AsyncTransaction

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.ports.repositories.ipassage_repository import (
    IPassageRepository,
)
from src.modules.catalog.domain.ports.repositories.itheme_repository import (
    IThemeRepository,
)
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    IWorkRepository,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.passage_repository import (
    PassageRepository,
)
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.theme_repository import (
    ThemeRepository,
)
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.work_repository import (
    WorkRepository,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.shared.infrastructure.persistence.neo4j.connection import (
    Neo4jConnectionHandler,
)
from src.shared.infrastructure.persistence.neo4j.units_of_work.base_unit_of_work import (
    BaseNeo4JUnitOfWork,
)


class Neo4jUnitOfWork(BaseNeo4JUnitOfWork, ICatalogGraphUnitOfWork):
    def __init__(
        self,
        connection_handler: Neo4jConnectionHandler,
        theme_mapper: IMapper[Mapping[str, Any], Theme],
        work_mapper: IMapper[Mapping[str, Any], Work] | None = None,
        author_mapper: IMapper[Mapping[str, Any], Author] | None = None,
        passage_mapper: IMapper[Mapping[str, Any], Passage] | None = None,
    ) -> None:
        super().__init__(connection_handler)
        self.__theme_mapper = theme_mapper
        self.__work_mapper = work_mapper
        self.__author_mapper = author_mapper
        self.__passage_mapper = passage_mapper
        self.__theme_repository: IThemeRepository | None = None
        self.__work_repository: IWorkRepository | None = None
        self.__passage_repository: IPassageRepository | None = None

    @property
    def theme_repository(self) -> IThemeRepository:
        if self.__theme_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__theme_repository

    @property
    def work_repository(self) -> IWorkRepository:
        if self.__work_repository is None:
            raise RuntimeError("Work repository is not available in this unit of work.")
        return self.__work_repository

    @property
    def passage_repository(self) -> IPassageRepository:
        if self.__passage_repository is None:
            raise RuntimeError(
                "Passage repository is not available in this unit of work."
            )
        return self.__passage_repository

    async def _init_repositories(self, transaction: AsyncTransaction) -> None:
        self.__theme_repository = ThemeRepository(transaction, self.__theme_mapper)
        if self.__work_mapper is not None and self.__author_mapper is not None:
            self.__work_repository = WorkRepository(
                transaction,
                self.__work_mapper,
                self.__author_mapper,
            )
        if self.__passage_mapper is not None:
            self.__passage_repository = PassageRepository(
                transaction,
                self.__passage_mapper,
            )

    async def _clear_repositories(self) -> None:
        self.__theme_repository = None
        self.__work_repository = None
        self.__passage_repository = None
