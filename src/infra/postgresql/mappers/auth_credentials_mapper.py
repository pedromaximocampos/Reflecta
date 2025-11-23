from src.domain.entities.user import AuthCredentials
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.domain.value_objects.password_algorithm import PasswordAlgorithm


class AuthCredentialsMapper:
    @staticmethod
    def to_model(auth_credentials: AuthCredentials) -> AuthCredentialsModel:
        return AuthCredentialsModel(
            user_id=auth_credentials.user_id.value,
            password_hash=auth_credentials.password.hash,
            password_algorithm=auth_credentials.password.algorithm.value,
            password_version=auth_credentials.password.version,
            created_at=auth_credentials.created_at,
            last_password_change=auth_credentials.last_password_change,
        )

    @staticmethod
    def to_entity(auth_credentials_model: AuthCredentialsModel) -> AuthCredentials:
        password = PasswordHash(
            hash=auth_credentials_model.password_hash,
            algorithm=PasswordAlgorithm(auth_credentials_model.password_algorithm),
            version=auth_credentials_model.password_version,
        )

        return AuthCredentials(
            user_id=UserId(auth_credentials_model.user_id),
            password=password,
            created_at=auth_credentials_model.created_at,
            last_password_change=auth_credentials_model.last_password_change,
        )