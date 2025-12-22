from src.domain.entities.reset_password import ResetPassword
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.models.reset_password_model import ResetPasswordModel


class ResetPasswordMapper:

    @staticmethod
    def to_entity(reset_password_model: ResetPasswordModel) -> ResetPassword:
        return ResetPassword(
            id=reset_password_model.id,
            user_id=UserId(reset_password_model.user_id),
            token_hash=reset_password_model.token_hash,
            expires_at=reset_password_model.expires_at,
            created_at=reset_password_model.created_at,
            used_at=reset_password_model.used_at,
        )

    @staticmethod
    def to_model(reset_password: ResetPassword) -> ResetPasswordModel:
        return ResetPasswordModel(
            id=reset_password.id,
            user_id=reset_password.user_id.value,
            token_hash=reset_password.token_hash,
            expires_at=reset_password.expires_at,
            created_at=reset_password.created_at,
            used_at=reset_password.used_at,
        )