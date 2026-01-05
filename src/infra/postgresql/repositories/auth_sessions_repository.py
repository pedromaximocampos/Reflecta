from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.auth_session import AuthSession
from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.token_jti import TokenJti
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel


class AuthSessionsRepository(IAuthSessionRepository):
    def __init__(
        self,
        session: AsyncSession,
        auth_session_mapper: AuthSessionsMapper,
        clock: IClock,
    ) -> None:
        self._session = session
        self._auth_session_mapper = auth_session_mapper
        self._clock = clock

    async def get_sessions_by_user_id(self, user_id: UserId) -> list[AuthSession]:
        query = (
            select(AuthSessionsModel)
            .where(
                AuthSessionsModel.user_id == user_id.value,
                AuthSessionsModel.revoked_at.is_(None),
                AuthSessionsModel.expires_at > self._clock.now(),
            )
            .order_by(AuthSessionsModel.issued_at.asc())
        )

        result = await self._session.execute(query)
        models: List[AuthSessionsModel] = result.scalars().all()
        return [self._auth_session_mapper.to_entity(m) for m in models]

    async def revoke_session(self, session_entity: AuthSession) -> None:
        """
        Marca uma sessão como revogada (revoked_at).
        Não faz commit (UoW controla).
        """
        query = (
            update(AuthSessionsModel)
            .where(AuthSessionsModel.id == session_entity.id)
            .values(revoked_at=session_entity.revoked_at)
        )
        await self._session.execute(query)

    async def create_session(self, session_entity: AuthSession) -> AuthSession:
        model: AuthSessionsModel = self._auth_session_mapper.to_model(session_entity)
        self._session.add(model)

        # INSERT sem commit
        await self._session.flush()
        await self._session.refresh(model)

        return self._auth_session_mapper.to_entity(model)

    async def get_session_by_hashed_jti(self, hashed_jti: TokenJti) -> Optional[AuthSession]:
        query = (
            select(AuthSessionsModel)
            .where(
                AuthSessionsModel.refresh_jti_hash == hashed_jti.value,
                AuthSessionsModel.revoked_at.is_(None),
                AuthSessionsModel.expires_at > self._clock.now(),
            )
        )

        result = await self._session.execute(query)
        model: Optional[AuthSessionsModel] = result.scalar_one_or_none()
        return None if model is None else self._auth_session_mapper.to_entity(model)

    async def invalidate_session(self, auth_session: AuthSession) -> None:
        """
        Invalida (revoga) a sessão no banco.
        Usa clock para revoked_at.
        Não comita.
        """
        query = (
            update(AuthSessionsModel)
            .where(AuthSessionsModel.id == auth_session.id)
            .values(revoked_at=self._clock.now())
        )
        await self._session.execute(query)

    async def refresh_session(self, auth_session: AuthSession) -> AuthSession:
        """
        Atualiza os campos do refresh (troca jti hash, issued/expires/updated).
        Retorna a sessão atualizada.
        Não comita.
        """
        query = (
            update(AuthSessionsModel)
            .where(
                AuthSessionsModel.id == auth_session.id,
                AuthSessionsModel.revoked_at.is_(None),
            )
            .values(
                refresh_jti_hash=auth_session.refresh_jti_hash.value,
                expires_at=auth_session.expires_at,
                updated_at=auth_session.updated_at,
            )
            .returning(AuthSessionsModel)
        )

        result = await self._session.execute(query)
        model = result.scalar_one()  # se não encontrou, lança (ok)
        return self._auth_session_mapper.to_entity(model)

    async def invalidate_all_sessions_for_user(self, user_id: UserId) -> None:
        """
        Invalida (revoga) todas as sessões ativas de um usuário.
        Usa clock para revoked_at.
        Não comita.
        """
        query = (
            update(AuthSessionsModel)
            .where(
                AuthSessionsModel.user_id == user_id.value,
                AuthSessionsModel.revoked_at.is_(None),
            )
            .values(revoked_at=self._clock.now())
        )
        await self._session.execute(query)