from src.modules.auth.domain.entities.user import User, AuthCredentials
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.auth.infrastructure.persistence.postgresql.models.auth_credentials_model import AuthCredentialsModel


class UserMapper(IMapper[UserModel, User]):
    def __init__(self, auth_credentials_mapper: IMapper[AuthCredentialsModel, AuthCredentials]):
        self.__auth_credentials_mapper = auth_credentials_mapper


    def to_entity(self, user_model: UserModel) -> User:

        auth_credentials_entity = self.__auth_credentials_mapper.to_entity(user_model.credentials)

        return User(
            id=UserId(user_model.id),
            email=Email(user_model.email),
            username=user_model.username,
            name=user_model.name,
            surname=user_model.surname,
            date_of_birth=user_model.date_of_birth,
            created_at=user_model.created_at,
            auth_credentials=auth_credentials_entity,
            avatar_url=user_model.avatar_url,
            last_login_at=user_model.last_login_at,
            is_email_verified=user_model.is_email_verified,
            email_verified_at=user_model.email_verified_at,
            role=user_model.role,
            deleted_at=user_model.deleted_at,
        )


    def to_model(self, user_entity: User) -> UserModel:

        user_model = UserModel(
            id=user_entity.id.value,
            email=user_entity.email.value,
            username=user_entity.username,
            name=user_entity.name,
            surname=user_entity.surname,
            date_of_birth=user_entity.date_of_birth,
            created_at=user_entity.created_at,
            avatar_url=user_entity.avatar_url,
            last_login_at=user_entity.last_login_at,
            is_email_verified=user_entity.is_email_verified,
            email_verified_at=user_entity.email_verified_at,
            role=user_entity.role,
            deleted_at=user_entity.deleted_at,
        )

        auth_credentials_model = self.__auth_credentials_mapper.to_model(user_entity.auth_credentials)
        auth_credentials_model.user_id = user_model.id

        user_model.credentials = auth_credentials_model


        return user_model
