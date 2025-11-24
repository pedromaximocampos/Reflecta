from typing import Protocol
from src.presentation.http_types.http_request import HttpRequest
from src.presentation.http_types.http_response import HttpResponse


class IControllerInterface(Protocol):

    async def handle_request(self, request: HttpRequest) -> HttpResponse: pass