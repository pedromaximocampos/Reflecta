from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.events.journal_entry_created import JournalEntryCreated
from src.modules.journal.domain.value_objects.journal_entry_status import JournalEntryStatus


def enqueue_created_entry(event: JournalEntryCreated, entry: JournalEntry) -> None:
    """Handle locally before commit: entry and durable pending work are atomic.

    The AI worker consumes pending entries after commit. Replaying this event
    must never reset a pending, failed, completed or deleted entry.
    """
    if (event.entry_id, event.user_id) != (entry.id, entry.user_id):
        raise ValueError("Event does not belong to this entry.")
    if entry.status is JournalEntryStatus.DRAFT and not entry.is_deleted:
        entry.mark_pending_analysis(now=event.occurred_at)
