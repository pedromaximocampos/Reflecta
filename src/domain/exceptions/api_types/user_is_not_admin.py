

class UserIsNotAdmin(Exception):
    """Exception raised when a user is not an admin."""

    def __init__(self, message="User is not an admin."):
        super().__init__()
        self.message = message
        self.status_code = 403
        self.name = "Forbidden"