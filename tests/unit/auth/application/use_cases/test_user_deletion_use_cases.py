from datetime import datetime, timedelta, timezone

import pytest

from src.modules.auth.application.services.user_deletion.user_deletion_service_impl import (
    UserDeletionServiceImpl,
)
from src.modules.auth.application.use_cases.delete.delete_user_use_case_impl import (
    DeleteUserUseCaseImpl,
)
from src.modules.auth.application.use_cases.request_delete.request_delete_use_case_impl import (
    RequestDeleteUseCaseImpl,
)
from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.domain.events.emails.user_deletion_requested import UserDeletionRequested
from src.modules.auth.domain.events.user_account_deleted import UserAccountDeleted
from src.modules.auth.domain.exceptions.user_deletion_exceptions import UserDeletionTokenError
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


class UsersRepositoryFake:
    def __init__(self, user) -> None:
        self.user = user
        self.deleted: tuple | None = None

    async def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id and not self.user.is_deleted:
            return self.user
        return None

    async def mark_as_deleted(self, user_id, deleted_at):
        self.deleted = (user_id, deleted_at)


class DeletionRepositoryFake:
    def __init__(self, request: UserDeletionRequest | None = None) -> None:
        self.request = request
        self.created: UserDeletionRequest | None = None
        self.revoked: UserDeletionRequest | None = None
        self.confirmed: tuple | None = None

    async def create(self, deletion_request):
        self.created = deletion_request
        self.request = deletion_request
        return deletion_request

    async def find_by_hashed_token(self, token_hash):
        if self.request is not None and self.request.token_hash == token_hash:
            return self.request
        return None

    async def get_active_by_user_id(self, user_id):
        request = self.request
        if (
            request is not None
            and request.user_id == user_id
            and not request.is_confirmed
            and not request.is_revoked
        ):
            return request
        return None

    async def revoke(self, deletion_request):
        self.revoked = deletion_request

    async def mark_as_confirmed(self, deletion_request, confirmed_at):
        self.confirmed = (deletion_request, confirmed_at)


class UnitOfWorkFake:
    def __init__(self, user, deletion_request=None) -> None:
        self.users_repository = UsersRepositoryFake(user)
        self.user_deletion_request_repository = DeletionRepositoryFake(deletion_request)
        self.auth_sessions_repository = object()
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

    async def persist_event(self, event, outbox_repo):
        self.events.append((event, outbox_repo))


class AuthSessionServiceSpy:
    def __init__(self) -> None:
        self.invalidated = []

    async def invalidate_all_sessions_for_user(self, user_id, uow):
        self.invalidated.append((user_id, uow))


@pytest.mark.asyncio
async def test_authenticated_request_persists_deletion_request_and_email_event() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    uow = UnitOfWorkFake(user)
    outbox = OutboxServiceSpy()
    use_case = RequestDeleteUseCaseImpl(
        auth_unit_of_work=uow,
        user_deletion_service=UserDeletionServiceImpl(
            system_clock=ClockFake(now=now),
            ulid_generator=UlidGeneratorFake(),
            hasher_generator=HasherFake(),
        ),
        outbox_service=outbox,
    )

    await use_case.execute(user.id)

    assert uow.user_deletion_request_repository.created is not None
    assert isinstance(outbox.events[0][0], UserDeletionRequested)
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_valid_code_soft_deletes_user_revokes_sessions_and_emits_event() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    deletion_request = UserDeletionRequest(
        id="01DELETIONREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:valid-code",
        created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=14),
    )
    uow = UnitOfWorkFake(user, deletion_request)
    sessions = AuthSessionServiceSpy()
    outbox = OutboxServiceSpy()
    use_case = DeleteUserUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        auth_session_service=sessions,
        outbox_service=outbox,
    )

    await use_case.execute("valid-code")

    assert user.deleted_at == now
    assert uow.users_repository.deleted == (user.id, now)
    assert uow.user_deletion_request_repository.confirmed == (deletion_request, now)
    assert sessions.invalidated == [(user.id, uow)]
    assert isinstance(outbox.events[0][0], UserAccountDeleted)
    assert outbox.events[0][0].to_payload() == {
        "user_id": user.id.value,
        "occurred_at": now.isoformat(),
    }
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_expired_code_does_not_delete_user_or_commit() -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    deletion_request = UserDeletionRequest(
        id="01DELETIONREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:expired-code",
        created_at=now - timedelta(minutes=20),
        expires_at=now,
    )
    uow = UnitOfWorkFake(user, deletion_request)
    use_case = DeleteUserUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        auth_session_service=AuthSessionServiceSpy(),
        outbox_service=OutboxServiceSpy(),
    )

    with pytest.raises(UserDeletionTokenError):
        await use_case.execute("expired-code")

    assert user.deleted_at is None
    assert uow.commits == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["confirmed", "revoked"])
async def test_used_or_revoked_code_cannot_be_reused(state: str) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = UserBuilder().build()
    request = UserDeletionRequest(
        id="01DELETIONREQUEST000000000",
        user_id=user.id,
        token_hash="hashed:used-code",
        created_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=14),
        confirmed_at=now if state == "confirmed" else None,
        revoked_at=now if state == "revoked" else None,
    )
    uow = UnitOfWorkFake(user, request)
    use_case = DeleteUserUseCaseImpl(
        auth_unit_of_work=uow,
        hasher_generator=HasherFake(),
        system_clock=ClockFake(now=now),
        auth_session_service=AuthSessionServiceSpy(),
        outbox_service=OutboxServiceSpy(),
    )

    with pytest.raises(UserDeletionTokenError):
        await use_case.execute("used-code")

    assert uow.commits == 0
