from datetime import date, datetime, timezone

import pytest

from src.modules.auth.application.services.email_verification.email_verification_service_impl import (
    EmailVerificationServiceImpl,
)
from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.auth.domain.entities.user import AuthCredentials, User
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.public.email import Email
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.public.user_id import UserId
from tests.support.doubles.clock_fake import ClockFake


class HasherFake:
    def generate_hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return hashed_text == self.generate_hash(plain_text)


class UlidGeneratorFake:
    def generate_ulid(self) -> str:
        return "01TESTEMAILVERIFICATION0"


class EmailVerificationRepositoryFake:
    def __init__(self) -> None:
        self.created: EmailVerification | None = None

    async def create_verification_code(
        self,
        email_verification: EmailVerification,
    ) -> EmailVerification:
        self.created = email_verification
        return email_verification


@pytest.mark.asyncio
async def test_verification_event_payload_contains_expiration_in_minutes() -> None:
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
        is_email_verified=False,
    )
    clock = ClockFake(now=now, email_verification_exp_seconds=15 * 60)
    repository = EmailVerificationRepositoryFake()
    service = EmailVerificationServiceImpl(
        hash_generator=HasherFake(),
        system_clock=clock,
        ulid_generator=UlidGeneratorFake(),
    )

    event = await service.create_email_verification_event(
        user,
        repository,
    )
    outbox_event = event.to_outbox_event(
        event_id="01TESTOUTBOXEVENT00000000",
        created_at=now,
    )

    assert repository.created is not None
    assert repository.created.expires_at == now.replace(minute=15)
    assert event.expires_in_minutes == 15
    assert outbox_event.payload["expires_in"] == 15
