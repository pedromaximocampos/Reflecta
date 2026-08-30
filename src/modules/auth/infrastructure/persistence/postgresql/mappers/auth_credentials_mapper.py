from src.modules.auth.domain.entities.user import AuthCredentials
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.modules.auth.public.password_algorithm import PasswordAlgorithm


class AuthCredentialsMapper(IMapper[AuthCredentialsModel, AuthCredentials]):

    def to_model(self, entity: AuthCredentials) -> AuthCredentialsModel:
        return AuthCredentialsModel(
            user_id=entity.user_id.value,
            password_hash=entity.password.hash,
            password_algorithm=entity.password.algorithm.value,
            password_version=entity.password.version,
            created_at=entity.created_at,
            last_password_change=entity.last_password_change,
        )


    def to_entity(self, model: AuthCredentialsModel) -> AuthCredentials:
        password = PasswordHash(
            hash=model.password_hash,
            algorithm=PasswordAlgorithm(model.password_algorithm),
            version=model.password_version,
        )

        return AuthCredentials(
            user_id=UserId(model.user_id),
            password=password,
            created_at=model.created_at,
            last_password_change=model.last_password_change,
        )