from datetime import datetime, timedelta, timezone

import pytest

from src.modules.auth.application.services.user_recovery.user_recovery_service_impl import (
    UserRecoveryServiceImpl,
)
from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from tests.support.builders.user_builder import UserBuilder
from tests.support.doubles.clock_fake import ClockFake


class HasherFake:
    def generate_hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"


class UlidGeneratorFake:
    def generate_ulid(self) -> str:
        return "01RECOVERYREQUEST000000000"


class RecoveryRepositoryFake:
    def __init__(self, active: UserRecoveryRequest | None = None) -> None:
        self.active = active
        self.created = None
        self.revoked = None

    async def get_active_by_user_id(self, user_id):
        return self.active if self.active and self.active.user_id == user_id else None

    async def create(self, request):
        self.created = request
        return request

    async def revoke(self, request):
        self.revoked = request


@pytest.mark.asyncio
async def test_issues_hashed_recovery_code_for_deleted_user() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().with_deleted_at(now - timedelta(days=1)).build()
    repository = RecoveryRepositoryFake()
    service = UserRecoveryServiceImpl(
        system_clock=ClockFake(now=now, user_recovery_exp_seconds=15 * 60),
        ulid_generator=UlidGeneratorFake(),
        hasher_generator=HasherFake(),
    )

    event = await service.issue_for_user(user, repository)

    assert repository.created.token_hash == f"hashed:{event.raw_code}"
    assert repository.created.token_hash != event.raw_code
    assert repository.created.expires_at == now + timedelta(minutes=15)
    assert event.to_payload()["expires_in"] == 15


@pytest.mark.asyncio
async def test_recovery_request_replaces_previous_active_code() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().with_deleted_at(now - timedelta(days=1)).build()
    previous = UserRecoveryRequest(
        id="01PREVIOUSRECOVERY00000000",
        user_id=user.id,
        token_hash="old-hash",
        created_at=now - timedelta(minutes=2),
        expires_at=now + timedelta(minutes=13),
    )
    repository = RecoveryRepositoryFake(active=previous)
    service = UserRecoveryServiceImpl(
        system_clock=ClockFake(now=now),
        ulid_generator=UlidGeneratorFake(),
        hasher_generator=HasherFake(),
    )

    await service.issue_for_user(user, repository)

    assert repository.revoked is previous
    assert previous.revoked_at == now
    assert repository.created is not None
