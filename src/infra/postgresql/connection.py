from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing import AsyncGenerator
from src.infra.postgresql.configs.settings import PostgresqlSettings


class DBConnectionHandler:
    __slots__ = ("_db_settings", "_engine", "_session_factory")

    def __init__(self, db_settings: PostgresqlSettings):
        """
        Inicializa o handler de conexão assíncrono com o banco PostgresSQL.
        """
        self._db_settings = db_settings

        self._engine: AsyncEngine = create_async_engine(
            self._db_settings.connection_string,
            echo=self._db_settings.echo,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Retorna o engine (para casos em que você precisa de conexão direta)."""
        return self._engine

    def get_session(self) -> AsyncSession:
        """Cria e retorna uma sessão (AsyncSession) manualmente."""
        return self._session_factory()

    @asynccontextmanager
    async def session(self )-> AsyncGenerator[AsyncSession, None]:
        """
        Cria um contexto gerenciado de sessão.
        Faz commit automático se não houver erro, rollback se houver exceção.

        Uso:
        async with db.session() as session:
            await session.execute(...)
        """
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self) -> None:
        """Fecha todas as conexões (útil em testes ou shutdown da aplicação)."""
        await self._engine.dispose()
