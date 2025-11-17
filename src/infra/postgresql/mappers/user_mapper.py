from src.domain.entities.user import User
from src.infra.postgresql.models.users_model import UserModel
from src.infra.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.infra.postgresql.mappers.auth_credentials_mapper import AuthCredentialsMapper


class UserMapper:
    @staticmethod
    def to_entity(user_model: UserModel, auth_credentials_model: AuthCredentialsModel) -> User:

        auth_credentials_entity = AuthCredentialsMapper.to_entity(auth_credentials_model)

        return User(
            id=user_model.id,
            email=user_model.email,
            username=user_model.username,
            name=user_model.name,
            surname=user_model.surname,
            date_of_birth=user_model.date_of_birth,
            created_at=user_model.created_at,
            auth_credentials=auth_credentials_entity,
            avatar_url=user_model.avatar_url,
            last_login_at=user_model.last_login_at,
        )


    @staticmethod
    def to_model(user_entity: User) -> tuple[UserModel, AuthCredentialsModel]:

        user_model = UserModel(
            id=user_entity.id,
            email=user_entity.email,
            username=user_entity.username,
            name=user_entity.name,
            surname=user_entity.surname,
            date_of_birth=user_entity.date_of_birth,
            created_at=user_entity.created_at,
            avatar_url=user_entity.avatar_url,
            last_login_at=user_entity.last_login_at,
        )

        auth_credentials_model = AuthCredentialsMapper.to_model(user_entity.auth_credentials)
        auth_credentials_model.user_id = user_model.id

        return user_model, auth_credentials_model