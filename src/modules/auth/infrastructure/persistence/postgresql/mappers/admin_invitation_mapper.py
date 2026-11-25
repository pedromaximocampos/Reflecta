from src.modules.auth.domain.entities.admin_invitation import AdminInvitation
from src.modules.auth.infrastructure.persistence.postgresql.models.admin_invitation_model import (
    AdminInvitationModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class AdminInvitationMapper(IMapper[AdminInvitationModel, AdminInvitation]):
    def to_entity(self, model: AdminInvitationModel) -> AdminInvitation:
        return AdminInvitation(
            id=model.id,
            target_user_id=UserId(model.target_user_id),
            invited_by_user_id=UserId(model.invited_by_user_id),
            target_email=model.target_email,
            target_username=model.target_username,
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            accepted_at=model.accepted_at,
            revoked_at=model.revoked_at,
        )

    def to_model(self, entity: AdminInvitation) -> AdminInvitationModel:
        return AdminInvitationModel(
            id=entity.id,
            target_user_id=entity.target_user_id.value,
            invited_by_user_id=entity.invited_by_user_id.value,
            target_email=entity.target_email,
            target_username=entity.target_username,
            token_hash=entity.token_hash,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            accepted_at=entity.accepted_at,
            revoked_at=entity.revoked_at,
        )
