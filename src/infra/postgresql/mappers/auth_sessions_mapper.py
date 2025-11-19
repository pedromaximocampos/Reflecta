from src.domain.entities.auth_session import AuthSession
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel

class AuthSessionsMapper:

    @staticmethod
    def to_model(auth_session: AuthSession) -> AuthSessionsModel:
        return AuthSessionsModel(
            id=auth_session.id,
            user_id=auth_session.user_id,
            issued_at=auth_session.issued_at,
            expires_at=auth_session.expires_at,
            refresh_jti_hash=auth_session.refresh_jti_hash,
            revoked_at=auth_session.revoked_at,
        )


    @staticmethod
    def to_entity(auth_session_model: AuthSessionsModel) -> AuthSession:
        return AuthSession(
            id=auth_session_model.id,
            user_id=auth_session_model.user_id,
            issued_at=auth_session_model.issued_at,
            expires_at=auth_session_model.expires_at,
            refresh_jti_hash=auth_session_model.refresh_jti_hash,
            revoked_at=auth_session_model.revoked_at,
        )