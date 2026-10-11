from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.ports.repositories import (
    IWorkIngestionChunkRepository,
)
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    WorkIngestionChunkModel,
)
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkIngestionChunkRepository(IWorkIngestionChunkRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[WorkIngestionChunkModel, WorkIngestionChunk],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create_many(
        self,
        chunks: Sequence[WorkIngestionChunk],
    ) -> tuple[WorkIngestionChunk, ...]:
        if not chunks:
            return ()
        values = [self._model_values(chunk) for chunk in chunks]
        statement = (
            postgresql_insert(WorkIngestionChunkModel)
            .values(values)
            .on_conflict_do_nothing(
                index_elements=["ingestion_id", "chunk_index"],
            )
        )
        await self.__session.execute(statement)
        await self.__session.flush()
        return await self.list_by_ingestion(chunks[0].ingestion_id)

    async def find_by_id(
        self,
        chunk_id: WorkIngestionChunkId,
    ) -> WorkIngestionChunk | None:
        result = await self.__session.execute(
            select(WorkIngestionChunkModel).where(
                WorkIngestionChunkModel.id == chunk_id.value
            )
        )
        model = result.scalar_one_or_none()
        return self.__mapper.to_entity(model) if model is not None else None

    async def list_by_ingestion(
        self,
        ingestion_id: WorkIngestionId,
        *,
        statuses: set[WorkIngestionChunkStatus] | None = None,
    ) -> tuple[WorkIngestionChunk, ...]:
        query = select(WorkIngestionChunkModel).where(
            WorkIngestionChunkModel.ingestion_id == ingestion_id.value
        )
        if statuses:
            query = query.where(
                WorkIngestionChunkModel.status.in_(
                    tuple(status.value for status in statuses)
                )
            )
        query = query.order_by(WorkIngestionChunkModel.chunk_index)
        result = await self.__session.execute(query)
        return tuple(self.__mapper.to_entity(model) for model in result.scalars())

    async def claim_next(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> WorkIngestionChunk | None:
        processable = or_(
            WorkIngestionChunkModel.status.in_(
                (
                    WorkIngestionChunkStatus.PENDING.value,
                    WorkIngestionChunkStatus.FAILED.value,
                )
            ),
            and_(
                WorkIngestionChunkModel.status
                == WorkIngestionChunkStatus.PROCESSING.value,
                WorkIngestionChunkModel.lease_expires_at <= now,
            ),
        )
        query = (
            select(WorkIngestionChunkModel)
            .where(
                WorkIngestionChunkModel.ingestion_id == ingestion_id.value,
                processable,
            )
            .order_by(WorkIngestionChunkModel.chunk_index)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        chunk = self.__mapper.to_entity(model)
        chunk.mark_processing(now=now, lease_expires_at=lease_expires_at)
        self._copy_mutable_state(model, chunk)
        await self.__session.flush()
        return self.__mapper.to_entity(model)

    async def update(
        self,
        chunk: WorkIngestionChunk,
    ) -> WorkIngestionChunk:
        query = (
            update(WorkIngestionChunkModel)
            .where(WorkIngestionChunkModel.id == chunk.id.value)
            .values(**self._mutable_values(chunk))
            .returning(WorkIngestionChunkModel)
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            raise LookupError(f"Work ingestion chunk '{chunk.id.value}' was not found.")
        return self.__mapper.to_entity(model)

    async def update_claimed(
        self,
        chunk: WorkIngestionChunk,
        *,
        expected_attempts: int,
    ) -> WorkIngestionChunk | None:
        query = (
            update(WorkIngestionChunkModel)
            .where(
                WorkIngestionChunkModel.id == chunk.id.value,
                WorkIngestionChunkModel.status
                == WorkIngestionChunkStatus.PROCESSING.value,
                WorkIngestionChunkModel.attempts == expected_attempts,
            )
            .values(**self._mutable_values(chunk))
            .returning(WorkIngestionChunkModel)
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        return self.__mapper.to_entity(model) if model is not None else None

    async def count_by_status(
        self,
        ingestion_id: WorkIngestionId,
    ) -> dict[WorkIngestionChunkStatus, int]:
        query = (
            select(
                WorkIngestionChunkModel.status,
                func.count(WorkIngestionChunkModel.id),
            )
            .where(WorkIngestionChunkModel.ingestion_id == ingestion_id.value)
            .group_by(WorkIngestionChunkModel.status)
        )
        result = await self.__session.execute(query)
        return {
            WorkIngestionChunkStatus(status): count for status, count in result.all()
        }

    @classmethod
    def _copy_mutable_state(
        cls,
        model: WorkIngestionChunkModel,
        chunk: WorkIngestionChunk,
    ) -> None:
        for name, value in cls._mutable_values(chunk).items():
            setattr(model, name, value)

    @staticmethod
    def _mutable_values(chunk: WorkIngestionChunk) -> dict[str, object]:
        return {
            "status": chunk.status.value,
            "attempts": chunk.attempts,
            "updated_at": chunk.updated_at,
            "started_at": chunk.started_at,
            "finished_at": chunk.finished_at,
            "lease_expires_at": chunk.lease_expires_at,
            "error_code": chunk.error_code,
            "error_message": chunk.error_message,
        }

    @classmethod
    def _model_values(cls, chunk: WorkIngestionChunk) -> dict[str, object]:
        return {
            "id": chunk.id.value,
            "ingestion_id": chunk.ingestion_id.value,
            "chunk_index": chunk.chunk_index,
            "start_page": chunk.start_page,
            "end_page": chunk.end_page,
            "start_offset": chunk.start_offset,
            "end_offset": chunk.end_offset,
            "content_sha256": chunk.content_sha256,
            "chunker_version": chunk.chunker_version,
            "created_at": chunk.created_at,
            **cls._mutable_values(chunk),
        }
