



class HttpResponse:
    def __init__(self, status_code: int, body: dict, headers: dict = None):
        self.status_code = status_code
        self.body = body
        self.headers = headers if headers is not None else {}

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "body": self.body,
        }