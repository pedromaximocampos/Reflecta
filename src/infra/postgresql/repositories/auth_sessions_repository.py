from src.domain.entities.auth_session import AuthSession
from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from sqlalchemy import select, update
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel
from typing import List, Optional


class AuthSessionsRepository(IAuthSessionRepository):

    def __init__(self, db: DBConnectionHandler, auth_session_mapper: AuthSessionsMapper, clock: IClock):
        self._db = db
        self._auth_session_mapper = auth_session_mapper
        self._clock = clock


    async def get_sessions_by_user_id(self, user_id: UserId) -> list[AuthSession]:
        async with self._db.session() as session:
            query = (
                select(AuthSessionsModel)
                .where(AuthSessionsModel.user_id == user_id,
                       AuthSessionsModel.revoked_at.is_(None),
                       AuthSessionsModel.expires_at > self._clock.now())

            )
            query = query.order_by(AuthSessionsModel.issued_at.asc())
            result = await session.execute(query)
            sessions_models: List[AuthSessionsModel] = result.scalars().all()

            return [self._auth_session_mapper.to_entity(model) for model in sessions_models]

    async def revoke_session(self, session_entity: AuthSession) -> None:
        async with self._db.session() as db_sess:
            model = await db_sess.get(AuthSessionsModel, session_entity.id)

            if model is None:
                return

            model.revoked_at = session_entity.revoked_at

        await db_sess.commit()


    async def create_session(self, session_entity: AuthSession) -> AuthSession:
        auth_session_model: AuthSessionsModel = self._auth_session_mapper.to_model(session_entity)

        async with self._db.session() as session:
            session.add(auth_session_model)
            await session.commit()
            await session.refresh(auth_session_model)

        return self._auth_session_mapper.to_entity(auth_session_model)

    async def get_session_by_hashed_jti(self, hashed_jti: str) -> Optional[AuthSession]:

        async with self._db.session() as session:
            query = (
                select(AuthSessionsModel)
                .where(AuthSessionsModel.refresh_jti_hash == hashed_jti,
                       AuthSessionsModel.revoked_at.is_(None),
                       AuthSessionsModel.expires_at > self._clock.now())
            )

            result = await session.execute(query)
            session_model: Optional[AuthSessionsModel] = result.scalar_one_or_none()

            if session_model is None:
                return None

            return self._auth_session_mapper.to_entity(session_model)

    async def invalidate_session(self, auth_session: AuthSession) -> None:
        async with self._db.session() as session:
            query =(
                update(AuthSessionsModel)
                .where(AuthSessionsModel.id == auth_session.id)
                .values(revoked_at=self._clock.now())
                .returning(AuthSessionsModel)
            )
            await session.execute(query)
            await session.commit()


    async def refresh_session(self, auth_session: AuthSession) -> AuthSession:
        async with self._db.session() as db_sess:
            query = (
                update(AuthSessionsModel)
                .where(
                    AuthSessionsModel.id == auth_session.id,
                    AuthSessionsModel.revoked_at.is_(None),
                       )
                .values(
                    refresh_jti_hash=auth_session.refresh_jti_hash.value,
                    issued_at=auth_session.issued_at,
                    expires_at=auth_session.expires_at,
                    updated_at=auth_session.updated_at,
                )
                .returning(AuthSessionsModel)
            )

            result = await db_sess.execute(query)
            await db_sess.commit()

            model = result.scalar_one()
            return self._auth_session_mapper.to_entity(model)