from src.application.services.auth_session import *
from src.domain.entities.user import User
from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.application.services.token.itoken_service import ITokenService
from src.domain.ports.system.iclock import IClock
from src.domain.entities.auth_session import AuthSession
from datetime import datetime, timezone
from src.application.services.token.dto import GeneratedTokenDTO
from src.domain.ports.system.iulid_generator import IULIDGenerator


class SessionServiceImpl(IAuthSessionService):

    _USER_SESSIONS_LIMIT = 5

    def __init__(self, session_repository: IAuthSessionRepository,clock: IClock, token_service: ITokenService, ulid_generator: IULIDGenerator) -> None:
        self._session_repository = session_repository
        self._token_service = token_service
        self._clock = clock
        self._ulid_generator = ulid_generator

    async def create_session(self, user: User) -> AuthSessionResultDTO:
        await self._check_sessions_limit(user.id)

        now = self._clock.now()

        access_token, refresh_token = self._generate_tokens_jwts(user, now)

        auth_session: AuthSession = AuthSession(
            id=self._ulid_generator.generate_ulid(),
            user_id=user.id,
            refresh_jti_hash=refresh_token.jti,
            issued_at=now,
            expires_at=refresh_token.expires_at,
        )

        created_auth_session: AuthSession = await self._session_repository.create_session(auth_session)

        return AuthSessionResultDTO(
            session_id=created_auth_session.id,
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )

    async def _check_sessions_limit(self, user_id: str) -> None:
        user_auth_sessions: list[AuthSession] = await self._session_repository.get_sessions_by_user_id(user_id)

        if len(user_auth_sessions) >= self._USER_SESSIONS_LIMIT:
            user_auth_sessions.sort(key=lambda auth_session: auth_session.issued_at)
            oldest_session: AuthSession = user_auth_sessions[0]
            oldest_session.revoke(revoked_at=self._clock.now())
            await self._session_repository.revoke_session(oldest_session)

    def _generate_tokens_jwts(self, user: User, now: datetime) -> tuple[GeneratedTokenDTO, GeneratedTokenDTO]:
        access_token_expiration = self._clock.access_token_expiration()
        refresh_token_expiration = self._clock.refresh_token_expiration()

        access_token: GeneratedTokenDTO = self._token_service.generate_token(user_id=user.id,
                                                               expires_in_seconds=access_token_expiration,
                                                               now=now)

        refresh_token: GeneratedTokenDTO = self._token_service.generate_token(user_id=user.id,
                                                                expires_in_seconds=refresh_token_expiration,
                                                                now=now)

        return access_token, refresh_token

    async def validate_session(self, session_id: str) -> AuthSessionResultDTO:
        pass
