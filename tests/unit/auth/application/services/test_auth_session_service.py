from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, call

import pytest

from src.modules.auth.application.ports.token.dto import GeneratedTokenDTO
from src.modules.auth.application.services.auth_session.auth_session_service_impl import (
    AuthSessionServiceImpl,
)
from src.modules.auth.domain.entities.auth_session import AuthSession
from src.modules.auth.domain.value_objects.token_jti import TokenJti
from src.modules.auth.public.user_id import UserId


@pytest.mark.asyncio
async def test_refresh_session_uses_injected_clock_and_rotates_tokens() -> None:
    now = datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc)
    user_id = UserId("01M4M1R7EQZFNJNPHF8DNE61JS")
    session = AuthSession(
        id="01M4M1T5EDQ3YVCVVC83J4EXCY",
        user_id=user_id,
        refresh_jti_hash=TokenJti("old-hash"),
        issued_at=now - timedelta(days=1),
        expires_at=now + timedelta(days=29),
    )
    access_token = GeneratedTokenDTO(
        jti=TokenJti("access-jti"),
        token="new-access-token",
        expires_at=now + timedelta(minutes=15),
    )
    refresh_token = GeneratedTokenDTO(
        jti=TokenJti("refresh-jti"),
        token="new-refresh-token",
        expires_at=now + timedelta(days=30),
    )
    clock = Mock()
    clock.now.return_value = now
    clock.access_token_expiration_in_seconds.return_value = 900
    clock.refresh_token_expiration_in_seconds.return_value = 2_592_000
    token_service = Mock()
    token_service.generate_token.side_effect = [access_token, refresh_token]
    hasher = Mock()
    hasher.generate_hash.return_value = "new-refresh-hash"
    repository = AsyncMock()
    repository.refresh_session.return_value = session
    uow = Mock()
    uow.auth_sessions_repository = repository
    service = AuthSessionServiceImpl(
        system_clock=clock,
        token_service=token_service,
        ulid_generator=Mock(),
        hasher_generator=hasher,
        max_sessions_per_user=5,
    )

    result = await service.refresh_session(session, uow)

    assert token_service.generate_token.call_args_list == [
        call(user_id=user_id, expires_in_seconds=900, now=now),
        call(user_id=user_id, expires_in_seconds=2_592_000, now=now),
    ]
    assert session.refresh_jti_hash == TokenJti("new-refresh-hash")
    assert session.expires_at == refresh_token.expires_at
    assert session.updated_at == now
    repository.refresh_session.assert_awaited_once_with(session)
    assert result.session_id == session.id
    assert result.access_token == "new-access-token"
    assert result.refresh_token == "new-refresh-token"
