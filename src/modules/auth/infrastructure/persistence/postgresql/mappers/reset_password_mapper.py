from src.modules.auth.domain.entities.reset_password import ResetPassword
from src.modules.auth.public.user_id import UserId
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models.reset_password_model import ResetPasswordModel


class ResetPasswordMapper(IMapper[ResetPasswordModel, ResetPassword]):


    def to_entity(self, model: ResetPasswordModel) -> ResetPassword:
        return ResetPassword(
            id=model.id,
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            used_at=model.used_at,
        )


    def to_model(self, entity: ResetPassword) -> ResetPasswordModel:
        return ResetPasswordModel(
            id=entity.id,
            user_id=entity.user_id.value,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            used_at=entity.used_at,
        )