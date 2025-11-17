

class ValidationFailed(Exception):
    """Raised when validation of data fails."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message
        self.status_code = 422
        self.name = "unprocessable Entity"
