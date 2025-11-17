


class NotFoundError(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message="Resource not found"):
        super().__init__()
        self.message = message
        self.status_code = 404
        self.name = "Not Found"