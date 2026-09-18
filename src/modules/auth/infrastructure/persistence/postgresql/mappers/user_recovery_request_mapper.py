from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from src.modules.auth.infrastructure.persistence.postgresql.models.user_recovery_request_model import (
    UserRecoveryRequestModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class UserRecoveryRequestMapper(IMapper[UserRecoveryRequestModel, UserRecoveryRequest]):
    def to_entity(self, model: UserRecoveryRequestModel) -> UserRecoveryRequest:
        return UserRecoveryRequest(
            id=model.id,
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            confirmed_at=model.confirmed_at,
            revoked_at=model.revoked_at,
        )

    def to_model(self, entity: UserRecoveryRequest) -> UserRecoveryRequestModel:
        return UserRecoveryRequestModel(
            id=entity.id,
            user_id=entity.user_id.value,
            token_hash=entity.token_hash,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            confirmed_at=entity.confirmed_at,
            revoked_at=entity.revoked_at,
        )
