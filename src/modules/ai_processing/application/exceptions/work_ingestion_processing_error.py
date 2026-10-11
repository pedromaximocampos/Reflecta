class WorkIngestionProcessingError(RuntimeError):
    pass


class WorkIngestionProcessingStorageError(WorkIngestionProcessingError):
    def __init__(self, operation: str) -> None:
        super().__init__(f"Work ingestion storage operation '{operation}' failed.")
        self.operation = operation


class WorkDocumentExtractionError(WorkIngestionProcessingError):
    pass


class WorkDocumentNormalizationError(WorkIngestionProcessingError):
    pass


class WorkDocumentChunkingError(WorkIngestionProcessingError):
    pass


class WorkPassageAnalysisError(WorkIngestionProcessingError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "work_passage_analysis_failed",
    ) -> None:
        normalized_code = code.strip()
        if not normalized_code or len(normalized_code) > 128:
            raise ValueError(
                "Work passage analysis error code must contain at most 128 characters."
            )
        super().__init__(message)
        self.code = normalized_code


class WorkIngestionConcurrentProcessingError(WorkIngestionProcessingError):
    pass


class InboxClaimLostError(WorkIngestionProcessingError):
    def __init__(self, event_id: str) -> None:
        super().__init__(f"Inbox claim for event '{event_id}' was lost.")
        self.event_id = event_id
