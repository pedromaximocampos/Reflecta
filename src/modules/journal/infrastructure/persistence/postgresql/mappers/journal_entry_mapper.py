from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class JournalEntryMapper(IMapper[JournalEntryModel, JournalEntry]):
    def to_entity(self, model: JournalEntryModel) -> JournalEntry:
        return JournalEntry(
            id=JournalEntryId(model.id),
            user_id=UserId(model.user_id),
            title=model.title,
            content_text=model.content_text,
            context_tags=model.context_tags,
            status=JournalEntryStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def to_model(self, entity: JournalEntry) -> JournalEntryModel:
        return JournalEntryModel(
            id=entity.id.value,
            user_id=entity.user_id.value,
            title=entity.title,
            content_text=entity.content_text,
            context_tags=entity.context_tags,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )
