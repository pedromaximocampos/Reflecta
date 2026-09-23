from datetime import datetime, timedelta, timezone

from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_deletion_request_mapper import (
    UserDeletionRequestMapper,
)
from src.modules.auth.public.user_id import UserId


def test_round_trip_preserves_user_deletion_request() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    entity = UserDeletionRequest(
        id="01DELETIONREQUEST000000000",
        user_id=UserId("01TESTUSER0000000000000000"),
        token_hash="hashed-token",
        created_at=now,
        expires_at=now + timedelta(minutes=15),
    )
    mapper = UserDeletionRequestMapper()

    mapped = mapper.to_entity(mapper.to_model(entity))

    assert mapped == entity
