from datetime import date, timedelta

from sqlalchemy import desc, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.exceptions.journal_exceptions import (
    JournalEntryDateConflictError,
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.ports.repositories.ijournal_entry_repository import (
    IJournalEntryRepository,
    JournalEntryCalendarItem,
    JournalEntryWindow,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class JournalEntryRepository(IJournalEntryRepository):
    _UPDATABLE_FIELDS = frozenset(
        {"title", "content_text", "context_tags"}
    )

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
                entry_date=model.entry_date,
                updated_at=model.updated_at,
                deleted_at=model.deleted_at,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    JournalEntryModel.user_id,
                    JournalEntryModel.entry_date,
                ],
                index_where=JournalEntryModel.deleted_at.is_(None),
            )
            .returning(JournalEntryModel)
        )
        result = await self.__session.execute(query)
        created_model = result.scalar_one_or_none()
        if created_model is not None:
            return self.__mapper.to_entity(created_model)

        existing = await self.find_by_date_for_user(
            journal_entry.entry_date,
            journal_entry.user_id,
        )
        if existing is None:
            raise RuntimeError("Journal entry date conflict could not be resolved.")
        raise JournalEntryDateConflictError(
            entry_id=existing.id.value,
            entry_date=existing.entry_date.isoformat(),
        )

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

    async def find_by_date_for_user(
        self,
        entry_date: date,
        user_id: UserId,
    ) -> JournalEntry | None:
        query = select(JournalEntryModel).where(
            JournalEntryModel.entry_date == entry_date,
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
            .order_by(
                desc(JournalEntryModel.entry_date),
                desc(JournalEntryModel.created_at),
                desc(JournalEntryModel.id),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.__session.execute(query)
        return [self.__mapper.to_entity(model) for model in result.scalars().all()]

    async def list_window_by_user(
        self,
        user_id: UserId,
        *,
        end_date: date | None,
        days: int,
        center_date: date | None = None,
        before_days: int = 15,
        after_days: int = 15,
    ) -> JournalEntryWindow:
        if not 1 <= days <= 31:
            raise ValueError("Journal window must contain between 1 and 31 days.")

        active_user_entry = (
            JournalEntryModel.user_id == user_id.value,
            JournalEntryModel.deleted_at.is_(None),
        )
        if center_date is not None:
            start_date = center_date - timedelta(days=before_days)
            anchor = center_date + timedelta(days=after_days)
        else:
            anchor = end_date
            start_date = None
        if anchor is None:
            anchor = await self.__session.scalar(
                select(func.max(JournalEntryModel.entry_date)).where(
                    *active_user_entry
                )
            )
        if anchor is None:
            return JournalEntryWindow((), None, None, None)

        if start_date is None:
            start_date = anchor - timedelta(days=days - 1)
        query = (
            select(JournalEntryModel)
            .where(
                *active_user_entry,
                JournalEntryModel.entry_date >= start_date,
                JournalEntryModel.entry_date <= anchor,
            )
            .order_by(
                desc(JournalEntryModel.entry_date),
                desc(JournalEntryModel.created_at),
                desc(JournalEntryModel.id),
            )
        )
        result = await self.__session.execute(query)
        entries = tuple(
            self.__mapper.to_entity(model) for model in result.scalars().all()
        )
        next_end_date = await self.__session.scalar(
            select(func.max(JournalEntryModel.entry_date)).where(
                *active_user_entry,
                JournalEntryModel.entry_date < start_date,
            )
        )
        return JournalEntryWindow(
            entries=entries,
            start_date=start_date,
            end_date=anchor,
            next_end_date=next_end_date,
        )

    async def list_calendar_by_user(
        self,
        user_id: UserId,
        *,
        start_date: date,
        end_date: date,
    ) -> tuple[JournalEntryCalendarItem, ...]:
        query = (
            select(
                JournalEntryModel.id,
                JournalEntryModel.entry_date,
                JournalEntryModel.status,
            )
            .where(
                JournalEntryModel.user_id == user_id.value,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.entry_date >= start_date,
                JournalEntryModel.entry_date <= end_date,
            )
            .order_by(JournalEntryModel.entry_date, JournalEntryModel.created_at)
        )
        result = await self.__session.execute(query)
        return tuple(
            JournalEntryCalendarItem(
                id=JournalEntryId(row.id),
                entry_date=row.entry_date,
                status=row.status,
            )
            for row in result.all()
        )

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
        values["status"] = journal_entry.status.value
        values["user_reprocess_count"] = 0
        values["processing_settings"] = None

        query = (
            update(JournalEntryModel)
            .where(
                JournalEntryModel.id == journal_entry.id.value,
                JournalEntryModel.user_id == journal_entry.user_id.value,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.status.in_(
                    ("draft", "analyzed", "analysis_failed")
                ),
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
