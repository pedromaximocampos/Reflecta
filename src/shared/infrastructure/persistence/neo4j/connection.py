from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import urlsplit

from neo4j import AsyncGraphDatabase, AsyncSession

from src.shared.infrastructure.persistence.neo4j.configs.settings import Neo4jConfig


class Neo4jConnectionHandler:
    def __init__(self, settings: Neo4jConfig) -> None:
        self._db_settings = settings
        driver_options = {}
        if urlsplit(self._db_settings.uri).scheme in {"bolt", "neo4j"}:
            driver_options["encrypted"] = self._db_settings.encrypted

        self._driver = AsyncGraphDatabase.driver(
            self._db_settings.uri,
            auth=(self._db_settings.user, self._db_settings.password),
            **driver_options,
        )

    def get_session(self) -> AsyncSession:
        return self._driver.session(
            database=self._db_settings.database,
        )

    async def verify_connection(self) -> None:
        """Verifica se a conexão com o banco de dados está ativa."""
        await self._driver.verify_connectivity()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._driver.session(database=self._db_settings.database) as session:
            yield session

    async def close(self) -> None:
        """Fecha todas as conexões (útil em testes ou shutdown da aplicação)."""
        await self._driver.close()
