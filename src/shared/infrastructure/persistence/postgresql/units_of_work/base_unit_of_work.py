from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Optional, Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler


class SQLAlchemyUnitOfWork(AbstractAsyncContextManager, ABC):
    """
    Base Unit of Work para SQLAlchemy (AsyncSession).

    Responsabilidades:
    - Abrir uma AsyncSession ao entrar no contexto.
    - Dar commit se não houver erro, rollback se houver.
    - Encerrar a sessão sempre ao final.
    - Delegar à subclasse a criação (bind) dos repositórios na session.
    """

    def __init__(self, db: DBConnectionHandler) -> None:
        self._db = db
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> Self:
        self._session = self._db.get_session()
        await self._init_repositories(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        assert self._session is not None
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._clear_repositories()

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()

    @abstractmethod
    async def _init_repositories(self, session: AsyncSession) -> None:
        """
            Inicializa os repositórios com a sessão fornecida.
            :param session: session criada pelo Unit of Work ao entrar no contexto
            :return: None
        """
        ...

    @abstractmethod
    def _clear_repositories(self) -> None:
        """
            Limpa as referências dos repositórios ao sair do contexto.
            :return: None
        """
        ...