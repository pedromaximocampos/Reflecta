from enum import Enum


class JournalEntryStatus(Enum):
    DRAFT = "draft"
    PENDING_ANALYSIS = "pending_analysis"
    ANALYZED = "analyzed"
    ANALYSIS_FAILED = "analysis_failed"