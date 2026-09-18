from collections.abc import Mapping
from typing import Any

from neo4j import AsyncTransaction

from src.modules.catalog.domain.entities.theme import Theme
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.modules.catalog.domain.ports.repositories.itheme_repository import IThemeRepository
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.theme_repository import ThemeRepository
from src.shared.infrastructure.persistence.neo4j.connection import Neo4jConnectionHandler
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import ICatalogGraphUnitOfWork
from src.shared.infrastructure.persistence.neo4j.units_of_work.base_unit_of_work import BaseNeo4JUnitOfWork


class Neo4jUnitOfWork(BaseNeo4JUnitOfWork, ICatalogGraphUnitOfWork):
    def __init__(
        self,
        connection_handler: Neo4jConnectionHandler,
        theme_mapper: IMapper[Mapping[str, Any], Theme],
    ) -> None:
        super().__init__(connection_handler)
        self.__theme_mapper = theme_mapper
        self.__theme_repository: IThemeRepository | None = None

    @property
    def theme_repository(self) -> IThemeRepository:
        if self.__theme_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__theme_repository

    async def _init_repositories(self, transaction: AsyncTransaction) -> None:
        self.__theme_repository = ThemeRepository(transaction, self.__theme_mapper)

    async def _clear_repositories(self) -> None:
        self.__theme_repository = None
