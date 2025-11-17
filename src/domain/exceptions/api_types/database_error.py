


class DatabaseError(Exception):
    """Exception raised for database-related errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Nao foi possivel conectar a LBC"):
        super().__init__()
        self.message = message
        self.status_code = 503
        self.name = "Database Error"