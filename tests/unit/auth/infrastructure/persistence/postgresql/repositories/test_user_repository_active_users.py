from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.postgresql.repositories.user_repository import (
    UserRepository,
)
from src.modules.auth.domain.value_objects.user_role import UserRole
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from tests.support.builders.user_builder import UserBuilder


def make_repository() -> tuple[UserRepository, AsyncMock]:
    session = AsyncMock(spec=AsyncSession)
    result = Mock()
    result.first.return_value = None
    session.execute.return_value = result
    mapper = Mock(spec=IMapper)
    return UserRepository(session, mapper), session


def compiled_sql(statement) -> str:
    return str(statement.compile(dialect=postgresql.dialect()))


@pytest.mark.asyncio
async def test_find_by_id_ignores_soft_deleted_users() -> None:
    repository, session = make_repository()

    await repository.find_by_id(UserId("01TESTUSER0000000000000000"))

    statement = session.execute.await_args.args[0]
    assert "users.deleted_at IS NULL" in compiled_sql(statement)


@pytest.mark.asyncio
async def test_find_by_email_ignores_soft_deleted_users() -> None:
    repository, session = make_repository()

    await repository.find_by_email(Email("user@example.com"))

    statement = session.execute.await_args.args[0]
    assert "users.deleted_at IS NULL" in compiled_sql(statement)


@pytest.mark.asyncio
async def test_recovery_lookup_by_email_selects_only_deleted_users() -> None:
    repository, session = make_repository()

    await repository.find_deleted_by_email(Email("user@example.com"))

    statement = session.execute.await_args.args[0]
    assert "users.deleted_at IS NOT NULL" in compiled_sql(statement)


@pytest.mark.asyncio
async def test_recovery_lookup_by_id_selects_only_deleted_users() -> None:
    repository, session = make_repository()

    await repository.find_deleted_by_id(UserId("01TESTUSER0000000000000000"))

    statement = session.execute.await_args.args[0]
    assert "users.deleted_at IS NOT NULL" in compiled_sql(statement)


@pytest.mark.asyncio
async def test_update_persists_role_and_soft_delete_timestamp() -> None:
    repository, session = make_repository()
    deleted_at = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = (
        UserBuilder()
        .with_role(UserRole.ADMIN)
        .with_deleted_at(deleted_at)
        .build()
    )

    await repository.update(user)

    statement = session.execute.await_args.args[0]
    compiled = statement.compile(dialect=postgresql.dialect())
    assert compiled.params["role"] is UserRole.ADMIN
    assert compiled.params["deleted_at"] == deleted_at
    assert "users.deleted_at IS NULL" in str(compiled)


@pytest.mark.asyncio
async def test_credentials_update_is_restricted_to_active_user() -> None:
    repository, session = make_repository()
    user = UserBuilder().build()

    await repository.update_auth_credentials(user)

    statement = session.execute.await_args.args[0]
    assert "users.deleted_at IS NULL" in compiled_sql(statement)


@pytest.mark.asyncio
async def test_user_info_update_changes_only_profile_columns() -> None:
    repository, session = make_repository()
    user = UserBuilder().build()

    await repository.update_user_info(user, frozenset({"name", "avatar_url"}))

    statement = session.execute.await_args.args[0]
    sql = compiled_sql(statement)
    set_clause = sql.split(" SET ", maxsplit=1)[1].split(" WHERE ", maxsplit=1)[0]
    assert "name=" in set_clause
    assert "avatar_url=" in set_clause
    assert "surname=" not in set_clause
    assert "date_of_birth=" not in set_clause
    assert "email=" not in set_clause
    assert "username=" not in set_clause
    assert "role=" not in set_clause
    assert "deleted_at=" not in set_clause
    assert "users.deleted_at IS NULL" in sql
