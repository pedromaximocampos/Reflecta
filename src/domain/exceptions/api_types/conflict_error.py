

class ConflictError(Exception):
    """Exception raised for conflicts in resource states.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Conflict occurred with the current state of the resource."):
        super().__init__()
        self.message = message
        self.status_code = 409
        self.name = "Conflict"
