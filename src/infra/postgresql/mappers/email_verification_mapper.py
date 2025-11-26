from src.domain.entities.email_verification import EmailVerification
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.models import UserEmailVerificationModel


class EmailVerificationMapper:

    @staticmethod
    def to_model(email_verification_entity:  EmailVerification) -> UserEmailVerificationModel:
        return UserEmailVerificationModel(
            id=email_verification_entity.id,
            user_id=email_verification_entity.user_id.value,
            token_hash=email_verification_entity.token_hash,
            created_at=email_verification_entity.created_at,
            expires_at=email_verification_entity.expires_at,
            verified_at=email_verification_entity.verified_at,
            revoked_at=email_verification_entity.revoked_at,
        )


    @staticmethod
    def to_entity(email_verification_model: UserEmailVerificationModel) -> EmailVerification:
        return EmailVerification(
            id=email_verification_model.id,
            user_id=UserId(email_verification_model.user_id),
            token_hash=email_verification_model.token_hash,
            created_at=email_verification_model.created_at,
            expires_at=email_verification_model.expires_at,
            verified_at=email_verification_model.verified_at,
            revoked_at=email_verification_model.revoked_at,
        )