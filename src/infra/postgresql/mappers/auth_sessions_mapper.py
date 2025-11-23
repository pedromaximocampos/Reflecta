from src.domain.entities.auth_session import AuthSession
from src.domain.value_objects.token_jti import TokenJti
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel

class AuthSessionsMapper:

    @staticmethod
    def to_model(auth_session: AuthSession) -> AuthSessionsModel:
        return AuthSessionsModel(
            id=auth_session.id,
            user_id=auth_session.user_id.value,
            issued_at=auth_session.issued_at,
            expires_at=auth_session.expires_at,
            refresh_jti_hash=auth_session.refresh_jti_hash.value,
            updated_at=auth_session.updated_at,
            revoked_at=auth_session.revoked_at,
        )


    @staticmethod
    def to_entity(auth_session_model: AuthSessionsModel) -> AuthSession:
        user_id = UserId(auth_session_model.user_id)
        refresh_jti_hash = TokenJti(auth_session_model.refresh_jti_hash)
        return AuthSession(
            id=auth_session_model.id,
            user_id=user_id,
            issued_at=auth_session_model.issued_at,
            expires_at=auth_session_model.expires_at,
            refresh_jti_hash=refresh_jti_hash,
            updated_at=auth_session_model.updated_at,
            revoked_at=auth_session_model.revoked_at,
        )