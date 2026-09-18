from src.modules.auth.domain.entities.auth_session import AuthSession
from src.modules.auth.domain.value_objects.token_jti import TokenJti
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models.auth_sessions_model import AuthSessionsModel

class AuthSessionsMapper(IMapper[AuthSessionsModel, AuthSession]):

    def to_model(self, entity: AuthSession) -> AuthSessionsModel:
        return AuthSessionsModel(
            id=entity.id,
            user_id=entity.user_id.value,
            issued_at=entity.issued_at,
            expires_at=entity.expires_at,
            refresh_jti_hash=entity.refresh_jti_hash.value,
            updated_at=entity.updated_at,
            revoked_at=entity.revoked_at,
        )


    def to_entity(self, model: AuthSessionsModel) -> AuthSession:
        user_id = UserId(model.user_id)
        refresh_jti_hash = TokenJti(model.refresh_jti_hash)
        return AuthSession(
            id=model.id,
            user_id=user_id,
            issued_at=model.issued_at,
            expires_at=model.expires_at,
            refresh_jti_hash=refresh_jti_hash,
            updated_at=model.updated_at,
            revoked_at=model.revoked_at,
        )
