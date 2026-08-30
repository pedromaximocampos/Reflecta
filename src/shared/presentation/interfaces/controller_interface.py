from typing import Protocol
from src.shared.presentation.http_types.http_request import HttpRequest
from src.shared.presentation.http_types.http_response import HttpResponse


class IControllerInterface(Protocol):

    async def handle_request(self, request: HttpRequest) -> HttpResponse: pass