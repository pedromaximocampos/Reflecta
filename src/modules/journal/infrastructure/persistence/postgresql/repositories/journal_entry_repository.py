from sqlalchemy import desc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.exceptions.journal_exceptions import (
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.ports.repositories.ijournal_entry_repository import (
    IJournalEntryRepository,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class JournalEntryRepository(IJournalEntryRepository):
    _UPDATABLE_FIELDS = frozenset({"title", "content_text", "context_tags"})

    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[JournalEntryModel, JournalEntry],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create(self, journal_entry: JournalEntry) -> JournalEntry:
        model = self.__mapper.to_model(journal_entry)
        query = (
            insert(JournalEntryModel)
            .values(
                id=model.id,
                user_id=model.user_id,
                title=model.title,
                content_text=model.content_text,
                context_tags=model.context_tags,
                status=model.status,
                created_at=model.created_at,
                updated_at=model.updated_at,
                deleted_at=model.deleted_at,
            )
            .returning(JournalEntryModel)
        )
        result = await self.__session.execute(query)
        return self.__mapper.to_entity(result.scalar_one())

    async def find_by_id_for_user(
        self,
        journal_entry_id: JournalEntryId,
        user_id: UserId,
    ) -> JournalEntry | None:
        query = select(JournalEntryModel).where(
            JournalEntryModel.id == journal_entry_id.value,
            JournalEntryModel.user_id == user_id.value,
            JournalEntryModel.deleted_at.is_(None),
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        return self.__mapper.to_entity(model) if model is not None else None

    async def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int,
        offset: int,
    ) -> list[JournalEntry]:
        query = (
            select(JournalEntryModel)
            .where(
                JournalEntryModel.user_id == user_id.value,
                JournalEntryModel.deleted_at.is_(None),
            )
            .order_by(desc(JournalEntryModel.created_at), desc(JournalEntryModel.id))
            .limit(limit)
            .offset(offset)
        )
        result = await self.__session.execute(query)
        return [self.__mapper.to_entity(model) for model in result.scalars().all()]

    async def update(
        self,
        journal_entry: JournalEntry,
        fields_to_update: frozenset[str],
    ) -> JournalEntry:
        if not fields_to_update or not fields_to_update.issubset(
            self._UPDATABLE_FIELDS
        ):
            raise ValueError("Invalid journal fields for update.")

        values = {
            field_name: getattr(journal_entry, field_name)
            for field_name in fields_to_update
        }
        values["updated_at"] = journal_entry.updated_at

        query = (
            update(JournalEntryModel)
            .where(
                JournalEntryModel.id == journal_entry.id.value,
                JournalEntryModel.user_id == journal_entry.user_id.value,
                JournalEntryModel.deleted_at.is_(None),
            )
            .values(**values)
            .returning(JournalEntryModel)
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            raise JournalEntryNotFoundError()
        return self.__mapper.to_entity(model)

    async def soft_delete(self, journal_entry: JournalEntry) -> None:
        query = (
            update(JournalEntryModel)
            .where(
                JournalEntryModel.id == journal_entry.id.value,
                JournalEntryModel.user_id == journal_entry.user_id.value,
                JournalEntryModel.deleted_at.is_(None),
            )
            .values(
                status=journal_entry.status.value,
                updated_at=journal_entry.updated_at,
                deleted_at=journal_entry.deleted_at,
            )
            .returning(JournalEntryModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise JournalEntryNotFoundError()
