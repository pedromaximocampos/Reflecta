from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.postgresql.repositories.user_recovery_request_repository import (
    UserRecoveryRequestRepository,
)
from src.modules.auth.public.user_id import UserId


@pytest.mark.asyncio
async def test_active_recovery_request_query_uses_user_id_value() -> None:
    session = AsyncMock(spec=AsyncSession)
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result
    repository = UserRecoveryRequestRepository(session=session, mapper=Mock())
    user_id = UserId("01TESTUSER0000000000000000")

    request = await repository.get_active_by_user_id(user_id)

    statement = session.execute.await_args.args[0]
    assert user_id.value in statement.compile().params.values()
    assert request is None
