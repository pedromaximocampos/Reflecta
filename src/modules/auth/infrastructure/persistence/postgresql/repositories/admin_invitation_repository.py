from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.admin_invitation import AdminInvitation
from src.modules.auth.domain.exceptions.admin_invitation_exceptions import (
    AdminInvitationTokenError,
)
from src.modules.auth.domain.ports.repositories.iadmin_invitation_repository import (
    IAdminInvitationRepository,
)
from src.modules.auth.infrastructure.persistence.postgresql.models.admin_invitation_model import (
    AdminInvitationModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class AdminInvitationRepository(IAdminInvitationRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[AdminInvitationModel, AdminInvitation],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create(self, invitation: AdminInvitation) -> AdminInvitation:
        model = self.__mapper.to_model(invitation)
        self.__session.add(model)
        await self.__session.flush()
        return self.__mapper.to_entity(model)

    async def find_by_hashed_token(self, token_hash: str) -> AdminInvitation | None:
        model = await self.__session.scalar(
            select(AdminInvitationModel).where(AdminInvitationModel.token_hash == token_hash)
        )
        return None if model is None else self.__mapper.to_entity(model)

    async def get_active_by_user_id(self, user_id: UserId) -> AdminInvitation | None:
        model = await self.__session.scalar(
            select(AdminInvitationModel)
            .where(
                AdminInvitationModel.target_user_id == user_id.value,
                AdminInvitationModel.accepted_at.is_(None),
                AdminInvitationModel.revoked_at.is_(None),
            )
            .with_for_update()
        )
        return None if model is None else self.__mapper.to_entity(model)

    async def get_by_id(self, invitation_id: str) -> AdminInvitation | None:
        model = await self.__session.scalar(
            select(AdminInvitationModel).where(AdminInvitationModel.id == invitation_id)
        )
        return None if model is None else self.__mapper.to_entity(model)

    async def list_recent(self, limit: int = 100) -> list[AdminInvitation]:
        models = (
            await self.__session.scalars(
                select(AdminInvitationModel)
                .order_by(AdminInvitationModel.created_at.desc())
                .limit(max(1, min(limit, 100)))
            )
        ).all()
        return [self.__mapper.to_entity(model) for model in models]

    async def revoke(self, invitation: AdminInvitation) -> None:
        await self.__session.execute(
            update(AdminInvitationModel)
            .where(
                AdminInvitationModel.id == invitation.id,
                AdminInvitationModel.accepted_at.is_(None),
                AdminInvitationModel.revoked_at.is_(None),
            )
            .values(revoked_at=invitation.revoked_at)
        )

    async def mark_as_accepted(self, invitation: AdminInvitation) -> None:
        result = await self.__session.execute(
            update(AdminInvitationModel)
            .where(
                AdminInvitationModel.id == invitation.id,
                AdminInvitationModel.accepted_at.is_(None),
                AdminInvitationModel.revoked_at.is_(None),
            )
            .values(accepted_at=invitation.accepted_at)
            .returning(AdminInvitationModel.id)
        )
        if result.scalar_one_or_none() is None:
            raise AdminInvitationTokenError()
