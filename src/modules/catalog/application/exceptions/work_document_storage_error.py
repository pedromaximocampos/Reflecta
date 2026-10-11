class WorkDocumentStorageError(RuntimeError):
    def __init__(self, operation: str) -> None:
        super().__init__(f"Work document storage operation failed: {operation}.")
        self.operation = operation
