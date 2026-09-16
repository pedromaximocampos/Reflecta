from datetime import datetime, timedelta, timezone

import pytest

from src.modules.auth.application.services.user_deletion.user_deletion_service_impl import (
    UserDeletionServiceImpl,
)
from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from tests.support.builders.user_builder import UserBuilder
from tests.support.doubles.clock_fake import ClockFake


class HasherFake:
    def generate_hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return hashed_text == self.generate_hash(plain_text)


class UlidGeneratorFake:
    def generate_ulid(self) -> str:
        return "01DELETIONREQUEST000000000"


class UserDeletionRepositoryFake:
    def __init__(self, active: UserDeletionRequest | None = None) -> None:
        self.active = active
        self.created: UserDeletionRequest | None = None
        self.revoked: UserDeletionRequest | None = None

    async def get_active_by_user_id(self, user_id):
        return self.active if self.active and self.active.user_id == user_id else None

    async def create(self, deletion_request):
        self.created = deletion_request
        return deletion_request

    async def revoke(self, deletion_request):
        self.revoked = deletion_request


@pytest.mark.asyncio
async def test_issues_hashed_single_use_deletion_code_and_email_event() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    repository = UserDeletionRepositoryFake()
    service = UserDeletionServiceImpl(
        system_clock=ClockFake(now=now, user_deletion_exp_seconds=15 * 60),
        ulid_generator=UlidGeneratorFake(),
        hasher_generator=HasherFake(),
    )

    event = await service.issue_for_user(user, repository)

    assert repository.created is not None
    assert repository.created.token_hash == f"hashed:{event.raw_code}"
    assert repository.created.token_hash != event.raw_code
    assert repository.created.expires_at == now + timedelta(minutes=15)
    assert event.expires_in_minutes == 15
    assert event.to_payload()["expires_in"] == 15


@pytest.mark.asyncio
async def test_revokes_previous_active_request_before_issuing_another() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    previous = UserDeletionRequest(
        id="01PREVIOUSDELETE0000000000",
        user_id=user.id,
        token_hash="old-hash",
        created_at=now - timedelta(minutes=2),
        expires_at=now + timedelta(minutes=13),
    )
    repository = UserDeletionRepositoryFake(active=previous)
    service = UserDeletionServiceImpl(
        system_clock=ClockFake(now=now),
        ulid_generator=UlidGeneratorFake(),
        hasher_generator=HasherFake(),
    )

    await service.issue_for_user(user, repository)

    assert repository.revoked is previous
    assert previous.revoked_at == now
    assert repository.created is not None
