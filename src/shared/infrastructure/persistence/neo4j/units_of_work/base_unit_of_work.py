from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self

from neo4j import AsyncSession, AsyncTransaction

from src.shared.infrastructure.persistence.neo4j.connection import Neo4jConnectionHandler


class BaseNeo4JUnitOfWork(AbstractAsyncContextManager, ABC):
    def __init__(self, connection_handler: Neo4jConnectionHandler) -> None:
        self._connection_handler = connection_handler
        self._session: AsyncSession | None = None
        self._transaction: AsyncTransaction | None = None

    async def __aenter__(self) -> Self:
        if self._session is not None or self._transaction is not None:
            raise RuntimeError("Unit of work is already active.")

        self._session = self._connection_handler.get_session()
        try:
            self._transaction = await self._session.begin_transaction()
            await self._init_repositories(self._transaction)
            return self
        except BaseException:
            try:
                if self._transaction is not None and not self._transaction.closed():
                    await self._transaction.rollback()
            finally:
                await self._session.close()
                self._session = None
                self._transaction = None
                await self._clear_repositories()
            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            if self._transaction is not None and not self._transaction.closed():
                await self.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._transaction = None
            await self._clear_repositories()

    async def commit(self) -> None:
        if self._transaction is None or self._transaction.closed():
            raise RuntimeError("Transaction is not started.")
        await self._transaction.commit()

    async def rollback(self) -> None:
        if self._transaction is None or self._transaction.closed():
            raise RuntimeError("Transaction is not started.")
        await self._transaction.rollback()

    @abstractmethod
    async def _init_repositories(self, transaction: AsyncTransaction) -> None:
        """Inicializa os repositórios usando a transação corrente."""
        ...

    @abstractmethod
    async def _clear_repositories(self) -> None:
        """Limpa as referências dos repositórios ao sair do contexto."""
        ...
