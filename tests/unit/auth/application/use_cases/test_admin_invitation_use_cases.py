from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from src.modules.auth.application.use_cases.admin_invitations import AdminInvitationUseCases
from src.modules.auth.domain.entities.admin_invitation import AdminInvitation
from src.modules.auth.domain.exceptions.admin_invitation_exceptions import (
    AdminInvitationTokenError,
)
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId


NOW = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)


class _Uow:
    def __init__(self) -> None:
        self.users_repository = AsyncMock()
        self.admin_invitation_repository = AsyncMock()
        self.outbox_repository = AsyncMock()
        self.commit = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None


def _clock():
    return SimpleNamespace(
        now=lambda: NOW,
        admin_invitation_expiration_in_seconds=lambda: 24 * 60 * 60,
    )


def _user(user_id: str, *, admin: bool, verified: bool = True):
    return SimpleNamespace(
        id=UserId(user_id),
        email=Email(f"{user_id.lower()}@example.com"),
        username=user_id,
        is_admin=admin,
        is_email_verified=verified,
        promote_to_admin=Mock(),
    )


def _use_cases(uow: _Uow):
    outbox = AsyncMock()
    service = AdminInvitationUseCases(
        auth_unit_of_work=uow,
        outbox_service=outbox,
        system_clock=_clock(),
        ulid_generator=SimpleNamespace(generate_ulid=lambda: "01ADMININVITATION000000000"),
        hasher_generator=SimpleNamespace(generate_hash=lambda value: f"hash:{value}"),
    )
    return service, outbox


@pytest.mark.asyncio
async def test_invitation_is_persisted_with_outbox_event_in_same_unit_of_work() -> None:
    uow = _Uow()
    admin = _user("01ADMIN000000000000000000", admin=True)
    target = _user("01TARGET00000000000000000", admin=False)
    uow.users_repository.find_by_id.return_value = admin
    uow.users_repository.find_by_email.return_value = target
    uow.admin_invitation_repository.get_active_by_user_id.return_value = None
    service, outbox = _use_cases(uow)

    result = await service.invite(target.email.value, admin.id.value)

    assert result["status"] == "PENDING"
    created = uow.admin_invitation_repository.create.await_args.args[0]
    assert created.target_user_id == target.id
    assert created.token_hash.startswith("hash:")
    event = outbox.persist_event.await_args.args[0]
    assert event.__event_type__ == "emails.admin_invitation.requested"
    assert event.user_email == target.email
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_accept_promotes_only_the_authenticated_recipient_and_consumes_token() -> None:
    uow = _Uow()
    target = _user("01TARGET00000000000000000", admin=False)
    invitation = AdminInvitation(
        id="01ADMININVITATION000000000",
        target_user_id=target.id,
        invited_by_user_id=UserId("01ADMIN000000000000000000"),
        target_email=target.email.value,
        target_username=target.username,
        token_hash="hash:secret",
        created_at=NOW,
        expires_at=NOW.replace(day=26),
    )
    uow.admin_invitation_repository.find_by_hashed_token.return_value = invitation
    uow.users_repository.find_by_id.return_value = target
    service, _ = _use_cases(uow)

    result = await service.accept("secret", target.id.value)

    assert result["role"] == "ADMIN"
    target.promote_to_admin.assert_called_once()
    uow.users_repository.promote_to_admin.assert_awaited_once_with(target.id)
    uow.admin_invitation_repository.mark_as_accepted.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_accept_rejects_a_different_authenticated_account() -> None:
    uow = _Uow()
    invitation = AdminInvitation(
        id="01ADMININVITATION000000000",
        target_user_id=UserId("01TARGET00000000000000000"),
        invited_by_user_id=UserId("01ADMIN000000000000000000"),
        target_email="target@example.com",
        target_username="target",
        token_hash="hash:secret",
        created_at=NOW,
        expires_at=NOW.replace(day=26),
    )
    uow.admin_invitation_repository.find_by_hashed_token.return_value = invitation
    service, _ = _use_cases(uow)

    with pytest.raises(AdminInvitationTokenError):
        await service.accept("secret", "01OTHER000000000000000000")

    uow.users_repository.promote_to_admin.assert_not_awaited()
    uow.commit.assert_not_awaited()
