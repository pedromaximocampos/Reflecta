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
        request_id: str | None = None,
        response_id: str | None = None,
    ) -> None:
        normalized_code = code.strip()
        if not normalized_code or len(normalized_code) > 128:
            raise ValueError(
                "Work passage analysis error code must contain at most 128 characters."
            )
        super().__init__(message)
        self.code = normalized_code
        self.request_id = request_id if request_id and request_id != "unknown" else None
        self.response_id = response_id if response_id and response_id != "unknown" else None


class WorkIngestionConcurrentProcessingError(WorkIngestionProcessingError):
    pass


class InboxClaimLostError(WorkIngestionProcessingError):
    def __init__(self, event_id: str) -> None:
        super().__init__(f"Inbox claim for event '{event_id}' was lost.")
        self.event_id = event_id
