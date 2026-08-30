from datetime import date, datetime, timezone

import pytest

from src.modules.auth.application.services.reset_password_service.password_reset_service_impl import (
    PasswordResetServiceImpl,
)
from src.modules.auth.domain.entities.reset_password import ResetPassword
from src.modules.auth.domain.entities.user import AuthCredentials, User
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.public.email import Email
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.public.user_id import UserId


class ClockFake:
    def __init__(self, now: datetime, expiration_seconds: int) -> None:
        self._now = now
        self._expiration_seconds = expiration_seconds

    def now(self) -> datetime:
        return self._now

    def password_reset_expiration_in_seconds(self) -> int:
        return self._expiration_seconds


class HasherFake:
    def generate_hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return hashed_text == self.generate_hash(plain_text)


class UlidGeneratorFake:
    def generate_ulid(self) -> str:
        return "01TESTPASSWORDRESET0000000"


class ResetPasswordRepositoryFake:
    def __init__(self) -> None:
        self.created: ResetPassword | None = None

    async def create_new_password_reset(
        self,
        reset_password: ResetPassword,
    ) -> ResetPassword:
        self.created = reset_password
        return reset_password


@pytest.mark.asyncio
async def test_password_reset_event_payload_contains_expiration_in_minutes() -> None:
    now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    user_id = UserId("01TESTUSER0000000000000000")
    user = User(
        id=user_id,
        email=Email("user@example.com"),
        username="test-user",
        name="Test",
        surname="User",
        date_of_birth=date(2000, 1, 1),
        created_at=now,
        auth_credentials=AuthCredentials(
            user_id=user_id,
            password=PasswordHash(
                hash="test-hash",
                algorithm=PasswordAlgorithm.ARGON2ID,
                version=1,
            ),
            created_at=now,
        ),
        is_email_verified=True,
    )
    repository = ResetPasswordRepositoryFake()
    service = PasswordResetServiceImpl(
        system_clock=ClockFake(now, 15 * 60),
        ulid_generator=UlidGeneratorFake(),
        hasher_generator=HasherFake(),
    )

    event = await service.issue_for_user(user, repository)
    outbox_event = event.to_outbox_event(
        event_id="01TESTOUTBOXEVENT00000000",
        created_at=now,
    )

    assert repository.created is not None
    assert event.expires_in_minutes == 15
    assert outbox_event.payload["expires_in"] == 15
