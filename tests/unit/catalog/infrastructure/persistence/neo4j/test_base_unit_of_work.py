from unittest.mock import AsyncMock, MagicMock

import pytest
from neo4j import AsyncTransaction

from src.shared.infrastructure.persistence.neo4j.units_of_work.base_unit_of_work import (
    BaseNeo4JUnitOfWork,
)


class ConcreteNeo4jUnitOfWork(BaseNeo4JUnitOfWork):
    def __init__(self, connection_handler) -> None:
        super().__init__(connection_handler)
        self.repository_initialized = False

    async def _init_repositories(self, transaction: AsyncTransaction) -> None:
        self.repository_initialized = True

    async def _clear_repositories(self) -> None:
        self.repository_initialized = False


class FailingNeo4jUnitOfWork(ConcreteNeo4jUnitOfWork):
    async def _init_repositories(self, transaction: AsyncTransaction) -> None:
        raise RuntimeError("repository initialization failed")


def make_uow():
    transaction = MagicMock()
    transaction.closed.return_value = False
    transaction.commit = AsyncMock()
    transaction.rollback = AsyncMock()

    async def commit() -> None:
        transaction.closed.return_value = True

    async def rollback() -> None:
        transaction.closed.return_value = True

    transaction.commit.side_effect = commit
    transaction.rollback.side_effect = rollback

    session = MagicMock()
    session.begin_transaction = AsyncMock(return_value=transaction)
    session.close = AsyncMock()

    connection_handler = MagicMock()
    connection_handler.get_session.return_value = session
    return ConcreteNeo4jUnitOfWork(connection_handler), connection_handler, session, transaction


@pytest.mark.asyncio
async def test_explicit_commit_is_not_followed_by_rollback() -> None:
    uow, _, session, transaction = make_uow()

    async with uow:
        assert uow.repository_initialized is True
        await uow.commit()

    transaction.commit.assert_awaited_once_with()
    transaction.rollback.assert_not_awaited()
    session.close.assert_awaited_once_with()
    assert uow.repository_initialized is False


@pytest.mark.asyncio
async def test_successful_exit_without_commit_rolls_back() -> None:
    uow, _, session, transaction = make_uow()

    async with uow:
        pass

    transaction.commit.assert_not_awaited()
    transaction.rollback.assert_awaited_once_with()
    session.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_exception_rolls_back_and_is_propagated() -> None:
    uow, _, session, transaction = make_uow()

    with pytest.raises(RuntimeError, match="failure"):
        async with uow:
            raise RuntimeError("failure")

    transaction.rollback.assert_awaited_once_with()
    session.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_repository_initialization_failure_releases_transaction_and_session() -> None:
    _, connection_handler, session, transaction = make_uow()
    failing_uow = FailingNeo4jUnitOfWork(connection_handler)

    with pytest.raises(RuntimeError, match="repository initialization failed"):
        await failing_uow.__aenter__()

    transaction.rollback.assert_awaited_once_with()
    session.close.assert_awaited_once_with()
