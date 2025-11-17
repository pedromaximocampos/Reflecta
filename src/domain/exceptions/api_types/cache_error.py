


class CacheError(Exception):
    """Exception raised for cache-related errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Nao foi possivel conectar com a LBC"):
        super().__init__()
        self.message = message
        self.status_code = 503
        self.name = "Cache Error"