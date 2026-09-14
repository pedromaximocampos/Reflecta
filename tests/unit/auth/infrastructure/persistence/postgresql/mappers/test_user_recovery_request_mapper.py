from datetime import datetime, timedelta, timezone

from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_recovery_request_mapper import (
    UserRecoveryRequestMapper,
)
from src.modules.auth.public.user_id import UserId


def test_round_trip_preserves_user_recovery_request() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    entity = UserRecoveryRequest(
        id="01RECOVERYREQUEST000000000",
        user_id=UserId("01TESTUSER0000000000000000"),
        token_hash="hashed-token",
        created_at=now,
        expires_at=now + timedelta(minutes=15),
    )
    mapper = UserRecoveryRequestMapper()

    assert mapper.to_entity(mapper.to_model(entity)) == entity
