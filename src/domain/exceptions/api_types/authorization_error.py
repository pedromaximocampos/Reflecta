

class AuthError(Exception):
    def __init__(self, message="Unauthorized access"):
        super().__init__()
        self.message = message
        self.status_code = 401
        self.name = "Unauthorized"