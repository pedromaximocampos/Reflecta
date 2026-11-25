import secrets
from datetime import timedelta

from src.modules.auth.domain.entities.admin_invitation import AdminInvitation
from src.modules.auth.domain.events.emails.admin_invitation_requested import (
    AdminInvitationRequested,
)
from src.modules.auth.domain.exceptions.admin_invitation_exceptions import (
    AdminInvitationAlreadyAdminError,
    AdminInvitationEmailNotVerifiedError,
    AdminInvitationForbiddenError,
    AdminInvitationNotFoundError,
    AdminInvitationStateError,
    AdminInvitationTargetNotFoundError,
    AdminInvitationTokenError,
)
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.modules.internal_events.public import IOutboxService
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class AdminInvitationUseCases:
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        outbox_service: IOutboxService,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
        hasher_generator: IHasherGenerator,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__outbox_service = outbox_service
        self.__clock = system_clock
        self.__ulid = ulid_generator
        self.__hasher = hasher_generator

    async def invite(self, email: str, invited_by_user_id: str) -> dict:
        normalized_email = Email(email)
        inviter_id = UserId(invited_by_user_id)
        async with self.__uow as uow:
            inviter = await uow.users_repository.find_by_id(inviter_id)
            if inviter is None or not inviter.is_admin:
                raise AdminInvitationForbiddenError()

            target = await uow.users_repository.find_by_email(normalized_email)
            if target is None:
                raise AdminInvitationTargetNotFoundError()
            if not target.is_email_verified:
                raise AdminInvitationEmailNotVerifiedError()
            if target.is_admin:
                raise AdminInvitationAlreadyAdminError()

            now = self.__clock.now()
            active = await uow.admin_invitation_repository.get_active_by_user_id(target.id)
            if active is not None:
                active.revoke(now)
                await uow.admin_invitation_repository.revoke(active)

            raw_code = secrets.token_urlsafe(32)
            expires_at = now + timedelta(
                seconds=self.__clock.admin_invitation_expiration_in_seconds()
            )
            invitation = AdminInvitation(
                id=self.__ulid.generate_ulid(),
                target_user_id=target.id,
                invited_by_user_id=inviter_id,
                target_email=target.email.value,
                target_username=target.username,
                token_hash=self.__hasher.generate_hash(raw_code),
                created_at=now,
                expires_at=expires_at,
            )
            await uow.admin_invitation_repository.create(invitation)
            await self.__outbox_service.persist_event(
                AdminInvitationRequested(
                    user_id=target.id,
                    username=target.username,
                    user_email=target.email,
                    raw_code=raw_code,
                    expires_in_minutes=int((expires_at - now).total_seconds() // 60),
                    occurred_at=now,
                ),
                uow.outbox_repository,
            )
            await uow.commit()
            return self.__serialize(invitation, now)

    async def list(self, requested_by_user_id: str) -> list[dict]:
        requester_id = UserId(requested_by_user_id)
        async with self.__uow as uow:
            requester = await uow.users_repository.find_by_id(requester_id)
            if requester is None or not requester.is_admin:
                raise AdminInvitationForbiddenError()
            now = self.__clock.now()
            invitations = await uow.admin_invitation_repository.list_recent()
            return [self.__serialize(invitation, now) for invitation in invitations]

    async def revoke(self, invitation_id: str, requested_by_user_id: str) -> dict:
        requester_id = UserId(requested_by_user_id)
        async with self.__uow as uow:
            requester = await uow.users_repository.find_by_id(requester_id)
            if requester is None or not requester.is_admin:
                raise AdminInvitationForbiddenError()
            invitation = await uow.admin_invitation_repository.get_by_id(invitation_id)
            if invitation is None:
                raise AdminInvitationNotFoundError()
            if invitation.is_accepted:
                raise AdminInvitationStateError()
            now = self.__clock.now()
            if not invitation.is_revoked:
                invitation.revoke(now)
                await uow.admin_invitation_repository.revoke(invitation)
                await uow.commit()
            return self.__serialize(invitation, now)

    async def accept(self, raw_code: str, authenticated_user_id: str) -> dict:
        if not raw_code or not raw_code.strip():
            raise AdminInvitationTokenError()
        user_id = UserId(authenticated_user_id)
        token_hash = self.__hasher.generate_hash(raw_code.strip())
        async with self.__uow as uow:
            invitation = await uow.admin_invitation_repository.find_by_hashed_token(token_hash)
            if invitation is None or invitation.target_user_id != user_id:
                raise AdminInvitationTokenError()
            now = self.__clock.now()
            if (
                invitation.is_accepted
                or invitation.is_revoked
                or invitation.is_expired(now)
            ):
                raise AdminInvitationTokenError()

            target = await uow.users_repository.find_by_id(user_id)
            if target is None or not target.is_email_verified or target.is_admin:
                raise AdminInvitationTokenError()

            invitation.accept(now)
            await uow.admin_invitation_repository.mark_as_accepted(invitation)
            target.promote_to_admin()
            try:
                await uow.users_repository.promote_to_admin(user_id)
            except UserNotFoundError as exc:
                raise AdminInvitationTokenError() from exc
            await uow.commit()
            return {
                "message": "Administrator invitation accepted successfully.",
                "role": "ADMIN",
            }

    @staticmethod
    def __serialize(invitation: AdminInvitation, now) -> dict:
        return {
            "id": invitation.id,
            "target_user_id": invitation.target_user_id.value,
            "target_email": invitation.target_email,
            "target_username": invitation.target_username,
            "invited_by_user_id": invitation.invited_by_user_id.value,
            "status": invitation.status_at(now),
            "created_at": invitation.created_at.isoformat(),
            "expires_at": invitation.expires_at.isoformat(),
            "accepted_at": (
                invitation.accepted_at.isoformat() if invitation.accepted_at else None
            ),
            "revoked_at": (
                invitation.revoked_at.isoformat() if invitation.revoked_at else None
            ),
        }
