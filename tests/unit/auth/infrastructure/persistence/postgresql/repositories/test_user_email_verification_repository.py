from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.postgresql.repositories.user_email_verification_repository import (
    UserEmailVerificationRepository,
)
from src.modules.auth.public.user_id import UserId


@pytest.mark.asyncio
async def test_active_verification_query_uses_user_id_value() -> None:
    session = AsyncMock(spec=AsyncSession)
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result
    repository = UserEmailVerificationRepository(
        session=session,
        mapper=Mock(),
    )
    user_id = UserId("01TESTUSER0000000000000000")

    verification = await repository.get_active_email_verification_by_user_id(user_id)

    statement = session.execute.await_args.args[0]
    assert user_id.value in statement.compile().params.values()
    assert str(user_id) not in statement.compile().params.values()
    assert verification is None
