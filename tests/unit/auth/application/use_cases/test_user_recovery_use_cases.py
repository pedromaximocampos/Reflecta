from datetime import datetime, timedelta, timezone

import pytest

from src.modules.auth.application.services.user_recovery.user_recovery_service_impl import (
    UserRecoveryServiceImpl,
)
from src.modules.auth.application.use_cases.recovery.recovery_use_case_impl import (
    RecoveryUseCaseImpl,
)
from src.modules.auth.application.use_cases.request_recovery.request_recovery_use_case_impl import (
    RequestRecoveryUseCaseImpl,
)
from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from src.modules.auth.domain.events.emails.user_recovery_requested import UserRecoveryRequested
from src.modules.auth.domain.events.user_account_recovered import UserAccountRecovered
from src.modules.auth.domain.exceptions.user_recovery_exceptions import UserRecoveryTokenError
from src.modules.auth.public.email import Email
from tests.support.builders.user_builder import UserBuilder
from tests.support.doubles.clock_fake import ClockFake


class HasherFake:
    def generate_hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"


class UlidGeneratorFake:
    def generate_ulid(self) -> str:
        return "01RECOVERYREQUEST000000000"


class UsersRepositoryFake:
    def __init__(self, user) -> None:
        self.user = user
        self.recovered = None

    async def find_deleted_by_email(self, email: Email):
        if self.user and self.user.email == email and self.user.is_deleted:
            return self.user
        return None

    async def find_deleted_by_id(self, user_id):
        if self.user and self.user.id == user_id and self.user.is_deleted:
            return self.user
        return None

    async def mark_as_recovered(self, user_id):
        self.recovered = user_id


class RecoveryRepositoryFake:
    def __init__(self, request=None) -> None:
        self.request = request
        self.created = None
        self.revoked = None
        self.confirmed = None

    async def create(self, request):
        self.request = request
        self.created = request
        return request

    async def find_by_hashed_token(self, token_hash):
        return self.request if self.request and self.request.token_hash == token_hash else None

    async def get_active_by_user_id(self, user_id):
        request = self.request
        if request and request.user_id == user_id and not request.is_confirmed and not request.is_revoked:
            return request
        return None

    async def revoke(self, request):
        self.revoked = request

    async def mark_as_confirmed(self, request, confirmed_at):
        self.confirmed = (request, confirmed_at)


class UnitOfWorkFake:
    def __init__(self, user, recovery_request=None) -> None:
        self.users_repository = UsersRepositoryFake(user)
        self.user_recovery_request_repository = RecoveryRepositoryFake(recovery_request)
        self.outbox_repository = object()
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        return None


class OutboxServiceSpy:
    def __init__(self) -> None:
        self.events = []

    async def persist_event(self, event, repository):
        self.events.append(event)


def make_request_use_case(uow, outbox, now):
    return RequestRecoveryUseCaseImpl(
        auth_unit_of_work=uow,
        user_recovery_service=UserRecoveryServiceImpl(
            system_clock=ClockFake(now=now),
            ulid_generator=UlidGeneratorFake(),
            hasher_generator=HasherFake(),
        ),
        outbox_service=outbox,
    )


@pytest.mark.asyncio
async def test_request_for_deleted_account_persists_code_and_email_event() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().with_deleted_at(now - timedelta(days=1)).build()
    uow = UnitOfWorkFake(user)
    outbox = OutboxServiceSpy()

    await make_request_use_case(uow, outbox, now).execute(user.email.value)

    assert uow.user_recovery_request_repository.created is not None
    assert isinstance(outbox.events[0], UserRecoveryRequested)
    assert uow.commits == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("user", [None, UserBuilder().build()])
async def test_request_does_not_reveal_missing_or_active_account(user) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    uow = UnitOfWorkFake(user)
    outbox = OutboxServiceSpy()

    await make_request_use_case(uow, outbox, now).execute("user@example.com")

    assert outbox.events == []
    assert uow.commits == 0


@pytest.mark.asyncio
async def test_valid_code_recovers_account_and_emits_event() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().with_deleted_at(now - timedelta(days=1)).build()
    request = UserRecoveryRequest(
        id="01RECOVERYREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:valid-code",
        created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=14),
    )
    uow = UnitOfWorkFake(user, request)
    outbox = OutboxServiceSpy()
    use_case = RecoveryUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        outbox_service=outbox,
    )

    await use_case.execute("valid-code")

    assert user.deleted_at is None
    assert uow.users_repository.recovered == user.id
    assert uow.user_recovery_request_repository.confirmed == (request, now)
    assert isinstance(outbox.events[0], UserAccountRecovered)
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_expired_code_does_not_recover_account() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    deleted_at = now - timedelta(days=1)
    user = UserBuilder().with_deleted_at(deleted_at).build()
    request = UserRecoveryRequest(
        id="01RECOVERYREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:expired-code",
        created_at=now - timedelta(minutes=20),
        expires_at=now,
    )
    uow = UnitOfWorkFake(user, request)
    use_case = RecoveryUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        outbox_service=OutboxServiceSpy(),
    )

    with pytest.raises(UserRecoveryTokenError):
        await use_case.execute("expired-code")

    assert user.deleted_at == deleted_at
    assert uow.commits == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["confirmed", "revoked"])
async def test_used_or_revoked_recovery_code_cannot_be_reused(state: str) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().with_deleted_at(now - timedelta(days=1)).build()
    request = UserRecoveryRequest(
        id="01RECOVERYREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:used-code",
        created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=14),
        confirmed_at=now if state == "confirmed" else None,
        revoked_at=now if state == "revoked" else None,
    )
    uow = UnitOfWorkFake(user, request)
    use_case = RecoveryUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        outbox_service=OutboxServiceSpy(),
    )

    with pytest.raises(UserRecoveryTokenError):
        await use_case.execute("used-code")

    assert uow.commits == 0


@pytest.mark.asyncio
async def test_valid_code_cannot_recover_an_account_that_is_already_active() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    request = UserRecoveryRequest(
        id="01RECOVERYREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:valid-code",
        created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=14),
    )
    uow = UnitOfWorkFake(user, request)
    use_case = RecoveryUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        outbox_service=OutboxServiceSpy(),
    )

    with pytest.raises(UserRecoveryTokenError):
        await use_case.execute("valid-code")

    assert uow.commits == 0
