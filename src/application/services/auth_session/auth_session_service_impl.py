from typing import Optional

from src.application.services.auth_session import *
from src.core.settings import get_settings
from src.domain.entities.user import User
from src.domain.exceptions.api_types import AuthError
from src.application.services.token.itoken_service import ITokenService
from src.domain.ports.system.iclock import IClock
from src.domain.entities.auth_session import AuthSession
from datetime import datetime, timezone
from src.application.services.token.dto import GeneratedTokenDTO
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.token_jti import TokenJti
from src.domain.value_objects.user_id import UserId

_settings = get_settings()

class AuthSessionServiceImpl(IAuthSessionService):


    _USER_SESSIONS_LIMIT = _settings.MAX_SESSIONS_PER_USER

    def __init__(self, clock: IClock, token_service: ITokenService,
                 ulid_generator: IULIDGenerator, jti_hasher_generator: IHasherGenerator) -> None:
        self._token_service = token_service
        self._clock = clock
        self._ulid_generator = ulid_generator
        self._jti_hasher_generator = jti_hasher_generator

    async def create_session(self, user: User, uow: IAuthUnitOfWork) -> AuthSessionResultDTO:
        await self._check_sessions_limit(user.id, uow)

        now = self._clock.now()

        access_token, refresh_token = self._generate_tokens_jwts(user, now)

        hashed_jti_refresh = self._jti_hasher_generator.generate_hash(refresh_token.jti.value)

        auth_session: AuthSession = AuthSession(
            id=self._ulid_generator.generate_ulid(),
            user_id=user.id,
            refresh_jti_hash=TokenJti(hashed_jti_refresh),
            issued_at=now,
            expires_at=refresh_token.expires_at,
        )

        created_auth_session: AuthSession = await uow.auth_sessions_repository.create_session(auth_session)

        return AuthSessionResultDTO(
            session_id=created_auth_session.id,
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )

    async def validate_session_by_refresh_token(self, refresh_jwt_token: str, uow: IAuthUnitOfWork) -> Optional[AuthSession]:
        try:
            decoded_refresh_token = self._token_service.validate_token(refresh_jwt_token)
        except AuthError:
            raise AuthError("Invalid refresh token")

        jti = decoded_refresh_token.get("jti")

        hashed_jti_refresh = self._jti_hasher_generator.generate_hash(jti)

        auth_session: Optional[AuthSession] = await uow.auth_sessions_repository.get_session_by_hashed_jti(
            TokenJti(hashed_jti_refresh)
        )

        return auth_session


    async def invalidate_all_sessions_for_user(self, user_id: UserId, uow: IAuthUnitOfWork) -> None:
        await uow.auth_sessions_repository.invalidate_all_sessions_for_user(user_id)


    async def invalidate_session(self, session: AuthSession, uow: IAuthUnitOfWork) -> None:
        await uow.auth_sessions_repository.invalidate_session(session)


    async def _check_sessions_limit(self, user_id: UserId, uow: IAuthUnitOfWork) -> None:
        user_auth_sessions: list[AuthSession] = await uow.auth_sessions_repository.get_sessions_by_user_id(user_id)

        if len(user_auth_sessions) >= self._USER_SESSIONS_LIMIT:
            oldest_session: AuthSession = user_auth_sessions[0]
            oldest_session.revoke(revoked_at=self._clock.now())
            await uow.auth_sessions_repository.revoke_session(oldest_session)

    def _generate_tokens_jwts(self, user: User, now: datetime) -> tuple[GeneratedTokenDTO, GeneratedTokenDTO]:
        access_token_expiration = self._clock.access_token_expiration_in_seconds()
        refresh_token_expiration = self._clock.refresh_token_expiration_in_seconds()

        access_token: GeneratedTokenDTO = self._token_service.generate_token(user_id=user.id,
                                                               expires_in_seconds=access_token_expiration,
                                                               now=now)

        refresh_token: GeneratedTokenDTO = self._token_service.generate_token(user_id=user.id,
                                                                expires_in_seconds=refresh_token_expiration,
                                                                now=now)

        return access_token, refresh_token


    async def refresh_session(self, session: AuthSession, uow: IAuthUnitOfWork) -> AuthSessionResultDTO:
        now = self._clock.now()

        new_access_token: GeneratedTokenDTO = self._token_service.generate_token(session.user_id, self._clock.access_token_expiration_in_seconds(), now)
        new_refresh_token: GeneratedTokenDTO = self._token_service.generate_token(session.user_id, self._clock.refresh_token_expiration_in_seconds(), now)

        hashed_jti_refresh = self._jti_hasher_generator.generate_hash(new_refresh_token.jti.value)

        session.refresh_jti_hash = TokenJti(hashed_jti_refresh)
        session.issued_at = now
        session.expires_at = new_refresh_token.expires_at
        session.updated_at = now


        refreshed_session: AuthSession = await uow.auth_sessions_repository.refresh_session(session)

        return AuthSessionResultDTO(
            session_id=refreshed_session.id,
            access_token=new_access_token.token,
            refresh_token=new_refresh_token.token,
        )

