from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.auth.public.user_id import UserId
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models import UserEmailVerificationModel


class EmailVerificationMapper(IMapper[UserEmailVerificationModel, EmailVerification]):


    def to_model(self, entity:  EmailVerification) -> UserEmailVerificationModel:
        return UserEmailVerificationModel(
            id=entity.id,
            user_id=entity.user_id.value,
            token_hash=entity.token_hash,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            verified_at=entity.verified_at,
            revoked_at=entity.revoked_at,
        )


    def to_entity(self, model: UserEmailVerificationModel) -> EmailVerification:
        return EmailVerification(
            id=model.id,
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            verified_at=model.verified_at,
            revoked_at=model.revoked_at,
        )