from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.infrastructure.persistence.postgresql.models.user_deletion_request_model import (
    UserDeletionRequestModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper


class UserDeletionRequestMapper(
    IMapper[UserDeletionRequestModel, UserDeletionRequest]
):
    def to_entity(self, model: UserDeletionRequestModel) -> UserDeletionRequest:
        return UserDeletionRequest(
            id=model.id,
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            confirmed_at=model.confirmed_at,
            revoked_at=model.revoked_at,
        )

    def to_model(self, entity: UserDeletionRequest) -> UserDeletionRequestModel:
        return UserDeletionRequestModel(
            id=entity.id,
            user_id=entity.user_id.value,
            token_hash=entity.token_hash,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            confirmed_at=entity.confirmed_at,
            revoked_at=entity.revoked_at,
        )
