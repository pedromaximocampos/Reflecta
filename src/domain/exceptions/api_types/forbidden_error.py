

class ForbiddenError(Exception):
    """Exception raised for forbidden access errors (HTTP 403)."""

    def __init__(self, message="Voce nao possui acesso liberado para utilizar o Gas Monitor contate a LBC, para ter o acesso completo."):
        super().__init__()
        self.message = message
        self.status_code = 403
        self.name = "Forbidden Error"