class UserAvatarStorageError(RuntimeError):
    def __init__(self, operation: str) -> None:
        super().__init__(f"User avatar storage operation failed: {operation}.")
        self.operation = operation
