from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.postgresql.connection import DBConnectionHandler


class SQLAlchemyUnitOfWork(ABC):
    """
    Base UoW: gerencia a transação (session/commit/rollback/close).
    Subclasses apenas "montam" os repositórios (bind na session).
    """

    def __init__(self, db: DBConnectionHandler) -> None:
        self._db = db
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self):
        """
        Inicia uma sessão pelo factory do DBConnectionHandler e inicializa os repositórios, toda vez que entrar no contexto.
        :return: Instancia do UnitOfWork com repositórios prontos para uso.
        """
        self._session = self._db.get_session()
        await self._init_repositories(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Finaliza o ciclo de vida da Unit of Work.

        - Se nenhuma exceção ocorreu durante o bloco 'async with', realiza o commit da transação.
        - Se ocorreu qualquer exceção, executa rollback para garantir atomicidade.
        - Em ambos os casos, a sessão é sempre encerrada ao final.

        :param exc_type: Tipo da exceção capturada (ou None se não houve erro).
        :param exc: Instância da exceção lançada.
        :param tb: Traceback associado à exceção.
        """
        assert self._session is not None
        try:
            if exc:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()

    @abstractmethod
    async def _init_repositories(self, session: AsyncSession) -> None:
        """
        Subclasse vai criar e expor repos bound à session.
        Ex: self.users = UserRepository(session, ...)
        """
        raise NotImplementedError
