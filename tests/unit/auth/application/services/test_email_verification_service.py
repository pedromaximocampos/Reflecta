from datetime import date, datetime, timedelta, timezone

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
    def __init__(self, active: EmailVerification | None = None) -> None:
        self.active = active
        self.created: EmailVerification | None = None
        self.revoked: EmailVerification | None = None

    async def create_verification_code(
        self,
        email_verification: EmailVerification,
    ) -> EmailVerification:
        self.created = email_verification
        return email_verification

    async def get_active_email_verification_by_user_id(
        self,
        user_id: UserId,
    ) -> EmailVerification | None:
        if self.active is not None and self.active.user_id == user_id:
            return self.active
        return None

    async def revoke(self, email_verification: EmailVerification) -> None:
        self.revoked = email_verification


def make_user(now: datetime) -> User:
    user_id = UserId("01TESTUSER0000000000000000")
    return User(
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


def make_service(now: datetime) -> EmailVerificationServiceImpl:
    return EmailVerificationServiceImpl(
        hash_generator=HasherFake(),
        system_clock=ClockFake(
            now=now,
            email_verification_exp_seconds=15 * 60,
        ),
        ulid_generator=UlidGeneratorFake(),
    )


@pytest.mark.asyncio
async def test_verification_event_payload_contains_expiration_in_minutes() -> None:
    now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    user = make_user(now)
    repository = EmailVerificationRepositoryFake()
    service = make_service(now)

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


@pytest.mark.asyncio
async def test_ensure_or_issue_keeps_an_active_non_expired_verification() -> None:
    now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    user = make_user(now)
    active_verification = EmailVerification(
        id="01ACTIVEVERIFICATION00000",
        user_id=user.id,
        token_hash="active-token-hash",
        created_at=now - timedelta(minutes=5),
        expires_at=now + timedelta(minutes=10),
    )
    repository = EmailVerificationRepositoryFake(active=active_verification)

    event = await make_service(now).ensure_or_issue(user, repository)

    assert event is None
    assert repository.created is None
    assert repository.revoked is None


@pytest.mark.asyncio
async def test_ensure_or_issue_revokes_expired_verification_before_issuing_new_one() -> None:
    now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    user = make_user(now)
    expired_verification = EmailVerification(
        id="01EXPIREDVERIFICATION0000",
        user_id=user.id,
        token_hash="expired-token-hash",
        created_at=now - timedelta(minutes=20),
        expires_at=now - timedelta(minutes=5),
    )
    repository = EmailVerificationRepositoryFake(active=expired_verification)

    event = await make_service(now).ensure_or_issue(user, repository)

    assert event is not None
    assert repository.revoked is expired_verification
    assert repository.revoked.revoked_at == now
    assert repository.created is not None
    assert repository.created.user_id == user.id
    assert repository.created.expires_at == now + timedelta(minutes=15)
