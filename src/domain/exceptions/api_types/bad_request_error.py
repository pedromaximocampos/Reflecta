
class BadRequestError(Exception):
    """Exception raised for bad requests.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Bad request"):
        super().__init__()
        self.message = message
        self.status_code = 400
        self.name = "Bad Request"