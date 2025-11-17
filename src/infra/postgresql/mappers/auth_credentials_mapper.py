from src.domain.entities.user import AuthCredentials
from src.infra.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.domain.value_objects.password_algorithm import PasswordAlgorithm


class AuthCredentialsMapper:
    @staticmethod
    def to_model(auth_credentials: AuthCredentials) -> AuthCredentialsModel:
        return AuthCredentialsModel(
            user_id=auth_credentials.user_id,
            password_hash=auth_credentials.password_hash,
            password_algorithm=auth_credentials.password_algorithm,
            password_version=auth_credentials.password_version,
            created_at=auth_credentials.created_at,
            last_password_change=auth_credentials.last_password_change,
        )

    @staticmethod
    def to_entity(auth_credentials_model: AuthCredentialsModel) -> AuthCredentials:
        return AuthCredentials(
            user_id=auth_credentials_model.user_id,
            password_hash=auth_credentials_model.password_hash,
            password_algorithm=PasswordAlgorithm(auth_credentials_model.password_algorithm),
            password_version=auth_credentials_model.password_version,
            created_at=auth_credentials_model.created_at,
            last_password_change=auth_credentials_model.last_password_change,
        )